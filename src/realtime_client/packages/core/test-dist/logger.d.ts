/**
 * Simple logger utility for Agent C Realtime SDK
 * Provides consistent logging with component prefixes
 */
export declare enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    NONE = 4
}
export declare class Logger {
    private static level;
    private prefix;
    constructor(component: string);
    static setLevel(level: LogLevel): void;
    debug(..._args: unknown[]): void;
    info(...args: unknown[]): void;
    warn(...args: unknown[]): void;
    error(...args: unknown[]): void;
}
