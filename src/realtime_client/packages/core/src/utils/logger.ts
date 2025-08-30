/**
 * Simple logger utility for Agent C Realtime SDK
 * Provides consistent logging with component prefixes
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4
}

export class Logger {
  private static level: LogLevel = LogLevel.INFO;
  private prefix: string;

  constructor(component: string) {
    this.prefix = `[${component}]`;
  }

  static setLevel(level: LogLevel): void {
    Logger.level = level;
  }

  debug(..._args: unknown[]): void {
    if (Logger.level <= LogLevel.DEBUG) {
      // console.debug(this.prefix, ...args);
    }
  }

  info(...args: unknown[]): void {
    if (Logger.level <= LogLevel.INFO) {
      console.warn(this.prefix, ...args);
    }
  }

  warn(...args: unknown[]): void {
    if (Logger.level <= LogLevel.WARN) {
      console.warn(this.prefix, ...args);
    }
  }

  error(...args: unknown[]): void {
    if (Logger.level <= LogLevel.ERROR) {
      console.error(this.prefix, ...args);
    }
  }
}