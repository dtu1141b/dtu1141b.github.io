document.addEventListener('DOMContentLoaded', function() {
  if (typeof mediumZoom !== 'undefined') {
    mediumZoom('.blog-image, .zoomable', {
      background: 'rgba(0, 0, 0, 0.9)',
      margin: 48,
      scrollOffset: 0,
      // Removed duration option - medium-zoom uses CSS transitions instead
      container: document.body,
      template: null
    });

    console.log('Image zoom initialized successfully');
  } else {
    console.warn('medium-zoom library not loaded. Image zoom will not work.');
  }
});
