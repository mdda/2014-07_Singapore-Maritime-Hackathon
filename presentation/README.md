
Pull in Reveal.js
------------------------------------
This additionally moves away the original reveal.js/index.html to reveal.js/index-orig.html,
so that your presentation can be the index.html for the reveal.js/ folder.

```
# in ./presentation
.... TODO ...
V=2.6.2
wget https://github.com/hakimel/reveal.js/archive/${V}.zip
unzip -t ${V}.zip
unzip ${V}.zip
mv reveal.js-${V}/index.html reveal.js-${V}/index-orig.html 
cp -R reveal.js-${V} reveal.js/
rm ${V}.zip
```

