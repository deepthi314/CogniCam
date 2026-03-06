import codecs

with codecs.open('F:/CogniCAM/cognicam/frontend/app.js', 'r', 'utf-16le') as f:
    text = f.read()

with codecs.open('F:/CogniCAM/cognicam/frontend/app.utf8.js', 'w', 'utf-8') as f:
    f.write(text)

with codecs.open('F:/CogniCAM/cognicam/frontend/index.html', 'r', 'utf-16le') as f:
    text = f.read()

with codecs.open('F:/CogniCAM/cognicam/frontend/index.utf8.html', 'w', 'utf-8') as f:
    f.write(text)
