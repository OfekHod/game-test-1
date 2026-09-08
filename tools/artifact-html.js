// Writes a copy of lane.html that is ready to publish as a Claude Artifact.
//
// The artifact host wraps whatever it is given in its own <!doctype>, <html>,
// <head> and <body> and adds the charset meta itself, so those lines are
// removed here. Everything else — the viewport meta, title, font links, style,
// markup and both scripts — is left byte for byte identical to the committed
// file, so what gets tested is what is in the repo.
//
// It refuses to run if lane.html does not start and end the way it expects,
// rather than quietly publishing something that differs from the source.
//
//   node tools/artifact-html.js <out.html>
const fs = require('fs');
const path = require('path');

const out = process.argv[2];
if(!out){ console.error('usage: node tools/artifact-html.js <out.html>'); process.exit(2); }

const src = path.join(__dirname, '..', 'lane.html');
let html = fs.readFileSync(src, 'utf8');

const HEAD_OPEN  = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n';
const HEAD_CLOSE = '\n</head>\n<body>\n';
const BODY_CLOSE = '\n</body>\n</html>\n';

function must(cond, msg){ if(!cond){ console.error('artifact-html: ' + msg); process.exit(1); } }
must(html.startsWith(HEAD_OPEN), 'lane.html does not start with the expected doctype/html/head/charset lines');
must(html.split(HEAD_CLOSE).length === 2, 'expected exactly one "</head><body>" boundary');
must(html.endsWith(BODY_CLOSE), 'lane.html does not end with </body></html>');

html = html.slice(HEAD_OPEN.length);
html = html.replace(HEAD_CLOSE, '\n');
html = html.slice(0, html.length - BODY_CLOSE.length) + '\n';

fs.writeFileSync(out, html);
console.log(`wrote ${out} (${Buffer.byteLength(html)} bytes) from ${src}`);
