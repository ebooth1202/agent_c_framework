from typing import Any, Optional, cast

from agent_c.prompting.prompt_section import PromptSection, property_bag_item



class WorkspacePlanSection(PromptSection):

    def __init__(self, **data: Any):
        TEMPLATE = ("The Workspace Plan Tool (wsp) allows to create and track plans using the metadata of a workspace\n"
                    "- Use a UNC style path of `//[workspace]/plans/[plan_id]` \n")
        super().__init__(template=TEMPLATE, required=True, name="Reverse Engineering", render_section_header=True, **data)

