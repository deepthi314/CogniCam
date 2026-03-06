const fs = require('fs');
['app.js', 'index.html'].forEach(file => {
  try {
    const buf = fs.readFileSync(file);
    let str = buf.toString('utf16le');
    if (str.charCodeAt(0) === 0xFEFF) str = str.slice(1);
    fs.writeFileSync(file + '.utf8', str, 'utf8');
    console.log('Converted ' + file);
  } catch (e) {
    console.error(e);
  }
});
