"use strict";
/**
 * Simple logger utility for Agent C Realtime SDK
 * Provides consistent logging with component prefixes
 */
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = exports.LogLevel = void 0;
var LogLevel;
(function (LogLevel) {
    LogLevel[LogLevel["DEBUG"] = 0] = "DEBUG";
    LogLevel[LogLevel["INFO"] = 1] = "INFO";
    LogLevel[LogLevel["WARN"] = 2] = "WARN";
    LogLevel[LogLevel["ERROR"] = 3] = "ERROR";
    LogLevel[LogLevel["NONE"] = 4] = "NONE";
})(LogLevel || (exports.LogLevel = LogLevel = {}));
var Logger = /** @class */ (function () {
    function Logger(component) {
        this.prefix = "[".concat(component, "]");
    }
    Logger.setLevel = function (level) {
        Logger.level = level;
    };
    Logger.prototype.debug = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
        if (Logger.level <= LogLevel.DEBUG) {
            // console.debug(this.prefix, ...args);
        }
    };
    Logger.prototype.info = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (Logger.level <= LogLevel.INFO) {
            console.warn.apply(console, __spreadArray([this.prefix], args, false));
        }
    };
    Logger.prototype.warn = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (Logger.level <= LogLevel.WARN) {
            console.warn.apply(console, __spreadArray([this.prefix], args, false));
        }
    };
    Logger.prototype.error = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (Logger.level <= LogLevel.ERROR) {
            console.error.apply(console, __spreadArray([this.prefix], args, false));
        }
    };
    Logger.level = LogLevel.INFO;
    return Logger;
}());
exports.Logger = Logger;
