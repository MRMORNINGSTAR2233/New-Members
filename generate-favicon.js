/**
 * Script to generate favicon files from SVG
 * This is a simple implementation - in production you might use tools like sharp or canvas
 */

const fs = require('fs');
const path = require('path');

// Create a simple HTML canvas-based favicon generator
const generateFaviconHTML = `
<!DOCTYPE html>
<html>
<head>
    <title>Favicon Generator</title>
</head>
<body>
    <canvas id="canvas16" width="16" height="16"></canvas>
    <canvas id="canvas32" width="32" height="32"></canvas>
    <canvas id="canvas180" width="180" height="180"></canvas>
    
    <script>
        function drawFavicon(canvas, size) {
            const ctx = canvas.getContext('2d');
            
            // Create gradient
            const gradient = ctx.createLinearGradient(0, 0, size, size);
            gradient.addColorStop(0, '#8B5CF6');
            gradient.addColorStop(0.5, '#3B82F6');
            gradient.addColorStop(1, '#06B6D4');
            
            // Draw rounded rectangle
            const radius = size * 0.25;
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.roundRect(0, 0, size, size, radius);
            ctx.fill();
            
            // Draw text
            ctx.fillStyle = 'white';
            ctx.font = \`bold \${size * 0.4}px system-ui, -apple-system, sans-serif\`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('ZB', size / 2, size / 2);
        }
        
        // Generate favicons
        drawFavicon(document.getElementById('canvas16'), 16);
        drawFavicon(document.getElementById('canvas32'), 32);
        drawFavicon(document.getElementById('canvas180'), 180);
        
        // Convert to data URLs and log them
        console.log('16x16:', document.getElementById('canvas16').toDataURL());
        console.log('32x32:', document.getElementById('canvas32').toDataURL());
        console.log('180x180:', document.getElementById('canvas180').toDataURL());
    </script>
</body>
</html>
`;

// Write the HTML file
fs.writeFileSync(path.join(__dirname, '../public/favicon-generator.html'), generateFaviconHTML);

console.log('Favicon generator HTML created at public/favicon-generator.html');
console.log('Open this file in a browser and check the console for data URLs');
console.log('Then manually save the canvas images as PNG files');
