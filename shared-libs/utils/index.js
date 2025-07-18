// Shared utilities for Claude projects

export const logger = {
  info: (message) => console.log(`[INFO] ${new Date().toISOString()}: ${message}`),
  error: (message) => console.error(`[ERROR] ${new Date().toISOString()}: ${message}`),
  warn: (message) => console.warn(`[WARN] ${new Date().toISOString()}: ${message}`)
};

export const formatDate = (date = new Date()) => {
  return date.toISOString().split('T')[0];
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};