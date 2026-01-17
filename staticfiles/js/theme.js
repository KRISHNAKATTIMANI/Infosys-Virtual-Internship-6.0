/**
 * Universal Theme Management System
 * Ensures consistent theme across all pages of AI Quiz Hub
 * 
 * Convention used throughout the app:
 * - 'light-mode' class on body = DARK theme (dark backgrounds, light text)
 * - No class on body = LIGHT theme (light backgrounds, dark text)
 * 
 * localStorage 'theme' values:
 * - 'dark' = dark theme (applies light-mode class)
 * - 'light' = light theme (removes light-mode class)
 */

(function() {
  'use strict';

  // Apply theme immediately to prevent flash
  function applyTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
    
    // Apply to documentElement immediately (always available)
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('light-mode');
    } else {
      document.documentElement.classList.remove('light-mode');
    }
    
    // Apply to body only if it exists
    if (document.body) {
      if (savedTheme === 'dark') {
        document.body.classList.add('light-mode');
      } else {
        document.body.classList.remove('light-mode');
      }
    }
    updateIcon();
  }

  // Update the theme toggle icon
  function updateIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      const themeIcon = themeToggle.querySelector('i');
      const isDark = document.body.classList.contains('light-mode');
      if (themeIcon) {
        // Sun icon in dark mode (click to go light), Moon icon in light mode (click to go dark)
        themeIcon.className = isDark ? 'ri-sun-line' : 'ri-moon-line';
      }
    }
  }

  // Run immediately
  applyTheme();

  // Setup theme toggle functionality when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    // Re-apply theme after DOM load (safety measure)
    applyTheme();

    // Find and setup theme toggle button
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      // Add click event listener
      themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('light-mode');
        document.documentElement.classList.toggle('light-mode');
        const isDark = document.body.classList.contains('light-mode');
        
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateIcon();
      });
    }
  });
})();
