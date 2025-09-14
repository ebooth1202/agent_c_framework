import copy
import pytest
from agent_c_tools.tools.workspace.executors.local_storage.validators.pnpm_validator import (
        PnpmCommandValidator,
    )


@pytest.fixture
def validator_pnpm():
    """Self-contained validator instance; no reliance on project-level fixtures."""
    return PnpmCommandValidator()
# ---------- Policy factory utilities ----------

def _deep_merge(a, b):
    """Shallow+dict-recursive merge for small policy dicts."""
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out

@pytest.fixture
def pnpm_policy_factory():
    """
    Returns a function that builds a minimal pnpm policy with optional overrides.

    Usage:
        pol_top = pnpm_policy_factory(overrides)
        pol = pol_top["pnpm"]
    """
    base = {
        "pnpm": {
            "validator": "pnpm",
            "root_flags": ["-v", "--version", "--help"],
            "default_timeout": 30,
            "subcommands": {}
        }
    }
    def _make(overrides=None):
        return _deep_merge(base, overrides or {})
    return _make


# ---------- Tests: parity without policy merging ----------

def test_parity_when_specs_identical(pnpm_policy_factory, validator_pnpm):
    """
    If build exists both as subcommand and run script with IDENTICAL spec,
    outcomes must match (same allow/deny, same suppress_success_output).
    """
    spec = {"allowed_flags": [], "suppress_success_output": True}
    pol_top = pnpm_policy_factory({
        "pnpm": {
            "subcommands": {
                "build": spec,
                "run": {"scripts": {"build": spec}}
            }
        }
    })
    pol = pol_top["pnpm"]

    r_sub = validator_pnpm.validate(["pnpm", "build"], pol)
    r_run = validator_pnpm.validate(["pnpm", "run", "build"], pol)

    assert r_sub.allowed and r_run.allowed
    assert bool(r_sub.policy_spec.get("suppress_success_output")) == \
           bool(r_run.policy_spec.get("suppress_success_output"))


def test_no_policy_merging_when_specs_different(pnpm_policy_factory, validator_pnpm):
    """
    If specs differ, outcomes can differ; validator must NOT merge/average settings.
    """
    pol_top = pnpm_policy_factory({
        "pnpm": {
            "subcommands": {
                "build": {"allowed_flags": [], "suppress_success_output": True},
                "run":   {"scripts": {
                    "build": {"allowed_flags": ["--ok-flag"], "suppress_success_output": False}
                }}
            }
        }
    })
    pol = pol_top["pnpm"]

    # Top-level: flags empty => block any flag
    bad_sub = validator_pnpm.validate(["pnpm", "build", "--x"], pol)
    assert not bad_sub.allowed

    # Run-script: only --ok-flag allowed
    ok_run  = validator_pnpm.validate(["pnpm", "run", "build", "--ok-flag"], pol)
    bad_run = validator_pnpm.validate(["pnpm", "run", "build", "--nope"], pol)
    assert ok_run.allowed and not bad_run.allowed

    # And they report different suppress_success_output values
    assert bool(ok_run.policy_spec.get("suppress_success_output", False)) is False


# ---------- Tests: allowed_flags semantics ----------

@pytest.mark.parametrize("script_spec, good, bad", [
    ({"allowed_flags": []}, [], ["--x"]),                          # present & empty => block all
    ({"allowed_flags": ["--a", "--b"]}, ["--a"], ["--z"]),        # present & non-empty => allow subset
    ({}, ["--whatever"], []),                                     # absent => unconstrained (we treat as allowed)
])
def test_allowed_flags_semantics(pnpm_policy_factory, validator_pnpm, script_spec, good, bad):
    pol_top = pnpm_policy_factory({
        "pnpm": {
            "subcommands": {"run": {"scripts": {"s": script_spec}}}
        }
    })
    pol = pol_top["pnpm"]

    # Baseline: no flags should be OK
    base = validator_pnpm.validate(["pnpm", "run", "s"], pol)
    assert base.allowed

    for f in good:
        res = validator_pnpm.validate(["pnpm", "run", "s", f], pol)
        assert res.allowed, f"Expected flag to be accepted: {f}"

    for f in bad:
        res = validator_pnpm.validate(["pnpm", "run", "s", f], pol)
        assert not res.allowed, f"Expected flag to be rejected: {f}"


# ---------- Tests: args + path safety matrix ----------

def test_deny_args_true_blocks_positionals(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"s": {"deny_args": True}}}}}
    })
    pol = pol_top["pnpm"]
    res = validator_pnpm.validate(["pnpm", "run", "s", "arg"], pol)
    assert not res.allowed


def test_allow_args_without_path_gate(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"s": {"deny_args": False}}}}}
    })
    pol = pol_top["pnpm"]
    res = validator_pnpm.validate(["pnpm", "run", "s", "arg"], pol)
    assert res.allowed


def test_allow_test_paths_only_within_workspace(pnpm_policy_factory, validator_pnpm, tmp_path, monkeypatch):
    ws = tmp_path / "w"
    (ws / "tests" / "unit").mkdir(parents=True)
    inside = str(ws / "tests" / "unit" / "a.spec.ts")
    escape = str(ws.parent / "etc" / "passwd")
    monkeypatch.setenv("WORKSPACE_ROOT", str(ws))

    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {
            "s": {"deny_args": False, "allow_test_paths": True}
        }}}}
    })
    pol = pol_top["pnpm"]

    ok_inside  = validator_pnpm.validate(["pnpm", "run", "s", inside], pol)
    bad_escape = validator_pnpm.validate(["pnpm", "run", "s", escape], pol)
    assert ok_inside.allowed and not bad_escape.allowed


# ---------- Tests: presence/absence scenarios ----------

def test_unknown_script_is_rejected(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"known": {}}}}}
    })
    pol = pol_top["pnpm"]
    res = validator_pnpm.validate(["pnpm", "run", "unknown"], pol)
    assert not res.allowed


def test_subcommand_only_vs_run_only(pnpm_policy_factory, validator_pnpm):
    # Case A: top-level only
    pol_top_A = pnpm_policy_factory({
        "pnpm": {"subcommands": {"build": {}, "run": {"scripts": {}}}}
    })
    polA = pol_top_A["pnpm"]
    assert validator_pnpm.validate(["pnpm", "build"], polA).allowed
    assert not validator_pnpm.validate(["pnpm", "run", "build"], polA).allowed

    # Case B: run-script only
    pol_top_B = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"build": {}}}}}
    })
    polB = pol_top_B["pnpm"]
    assert validator_pnpm.validate(["pnpm", "run", "build"], polB).allowed
    assert not validator_pnpm.validate(["pnpm", "build"], polB).allowed


# ---------- Optional: root flags sanity ----------

def test_root_flags_behavior(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory({
        "pnpm": {"root_flags": ["--version"], "subcommands": {}}
    })
    pol = pol_top["pnpm"]
    assert validator_pnpm.validate(["pnpm", "--version"], pol).allowed
    # A non-root flag should NOT be treated as a subcommand
    r = validator_pnpm.validate(["pnpm", "--definitely-not-root-flag"], pol)
    assert not r.allowed

def test_end_of_options_separator_respected(pnpm_policy_factory, validator_pnpm):
    # deny_args: true should still reject positionals after '--'
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"s": {"deny_args": True}}}}}
    })
    pol = pol_top["pnpm"]

    ok = validator_pnpm.validate(["pnpm","run","s"], pol)
    assert ok.allowed

    # After '--' we pass "positional" tokens that start with '-'
    bad = validator_pnpm.validate(["pnpm","run","s","--","-we-are-positional-now"], pol)
    assert not bad.allowed


def test_end_of_options_with_allowed_args(pnpm_policy_factory, validator_pnpm):
    # deny_args:false + allow_test_paths:false => args allowed after '--'
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"s": {"deny_args": False}}}}}
    })
    pol = pol_top["pnpm"]

    res = validator_pnpm.validate(["pnpm","run","s","--","-still-positional"], pol)
    assert res.allowed


def test_script_name_that_looks_like_flag(pnpm_policy_factory, validator_pnpm):
    # Ensure a script named '--report' is recognized as the script when '--' separator used
    pol_top = pnpm_policy_factory({
        "pnpm": {"subcommands": {"run": {"scripts": {"--report": {"deny_args": True}}}}}
    })
    pol = pol_top["pnpm"]

    # Without separator, first non-flag token is the script, so this should fail (no non-flag token)
    bad = validator_pnpm.validate(["pnpm","run","--report"], pol)
    assert not bad.allowed

    # With separator, we can explicitly pass the script name after '--'
    ok = validator_pnpm.validate(["pnpm","run","--","--report"], pol)
    assert ok.allowed

# --- Global flags before subcommand: behavior tests ---

def _policy_with_globals(extra: dict = None):
    base = {
        "pnpm": {
            "global_flags_before_subcommand": {
                "--filter": True,            # requires a value
                "--workspace-root": False,   # boolean (no value)
                "-r": False,                 # alias for --recursive
            },
            "subcommands": {}
        }
    }
    if extra:
        # shallow merge for convenience in tests
        base["pnpm"]["subcommands"].update(extra.get("pnpm", {}).get("subcommands", {}))
        # allow test to override/extend global flags too
        gf = extra.get("pnpm", {}).get("global_flags_before_subcommand")
        if gf:
            base["pnpm"]["global_flags_before_subcommand"].update(gf)
    return base


def test_global_flag_filter_then_subcommand_ok(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory(_policy_with_globals({
        "pnpm": {"subcommands": {"test": {"allow_test_paths": True, "deny_args": False}}}
    }))
    pol = pol_top["pnpm"]

    # space form
    r1 = validator_pnpm.validate(["pnpm", "--filter", "@agentc/realtime-ui", "test", "src/foo.test.ts"], pol)
    assert r1.allowed

    # equals form
    r2 = validator_pnpm.validate(["pnpm", "--filter=@agentc/realtime-ui", "test"], pol)
    assert r2.allowed


def test_multiple_globals_then_run_script_args_ok(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory(_policy_with_globals({
        "pnpm": {"subcommands": {
            "run": {"scripts": {"s": {"deny_args": False}}}
        }}
    }))
    pol = pol_top["pnpm"]

    cmd = ["pnpm", "--workspace-root", "--filter", "@agentc/realtime-ui", "run", "s", "--", "arg1"]
    r = validator_pnpm.validate(cmd, pol)
    assert r.allowed


def test_missing_value_for_global_flag_is_error(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory(_policy_with_globals({
        "pnpm": {"subcommands": {"test": {}}}
    }))
    pol = pol_top["pnpm"]

    # --filter requires a value; here it's missing (next token is the subcommand)
    r = validator_pnpm.validate(["pnpm", "--filter", "test"], pol)
    assert not r.allowed


def test_disallowed_global_flag_rejected(pnpm_policy_factory, validator_pnpm):
    # No global_flags_before_subcommand -> treat --filter as a root flag (not in root_flags) -> reject
    pol_top = pnpm_policy_factory({
        "pnpm": {
            "root_flags": ["-v", "--version", "--help"],
            "subcommands": {"test": {}}
        }
    })
    pol = pol_top["pnpm"]

    r = validator_pnpm.validate(["pnpm", "--filter", "@agentc/realtime-ui", "test"], pol)
    assert not r.allowed


def test_globals_do_not_merge_policies(pnpm_policy_factory, validator_pnpm):
    # Top-level build forbids flags (allowed_flags: []), run:build allows --ok-flag only
    pol_top = pnpm_policy_factory(_policy_with_globals({
        "pnpm": {"subcommands": {
            "build": {"allowed_flags": []},
            "run":   {"scripts": {"build": {"allowed_flags": ["--ok-flag"], "deny_args": False}}}
        }}
    }))
    pol = pol_top["pnpm"]

    ok = validator_pnpm.validate(["pnpm", "--filter", "@scope/pkg", "run", "build", "--ok-flag"], pol)
    assert ok.allowed

    bad = validator_pnpm.validate(["pnpm", "--filter", "@scope/pkg", "build", "--ok-flag"], pol)
    assert not bad.allowed  # still top-level build policy (no flags), not merged


def test_globals_preserve_deny_args_for_run_scripts(pnpm_policy_factory, validator_pnpm):
    pol_top = pnpm_policy_factory(_policy_with_globals({
        "pnpm": {"subcommands": {
            "run": {"scripts": {"s": {"deny_args": True}}}
        }}
    }))
    pol = pol_top["pnpm"]

    # Positionals after script (even after '--') are rejected when deny_args: true
    r = validator_pnpm.validate(["pnpm", "--filter", "@agentc/realtime-ui", "run", "s", "--", "pos"], pol)
    assert not r.allowed
