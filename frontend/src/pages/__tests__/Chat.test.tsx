import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, jest } from '@jest/globals';
import { Chat } from '../Chat';

// Mock the API client
jest.mock('../../api/client', () => ({
  api: {
    sendMessage: jest.fn(() => Promise.resolve({ response: 'Test response' })),
    sendChatMessage: jest.fn(() => Promise.resolve({})),
    switchRole: jest.fn(() => Promise.resolve({})),
    getRoleHistory: jest.fn(() => Promise.resolve([])),
  },
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Send: () => null,
  Bot: () => null,
  User: () => null,
  Sparkles: () => null,
  X: () => null,
}));

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

// Mock getBoundingClientRect
Element.prototype.getBoundingClientRect = jest.fn(() => ({
  width: 0,
  height: 0,
  top: 0,
  left: 0,
  bottom: 0,
  right: 0,
}));

describe('Chat Component', () => {
  it('renders without crashing', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => render(<Chat />)).not.toThrow();
    
    consoleSpy.mockRestore();
  });
});
