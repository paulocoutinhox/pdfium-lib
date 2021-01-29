// This makes sure the generated module is easily able
// to locate the '.wasm' file when running in node.
Module = {
    locateFile: function (name) {
        return require('path').join(__dirname, name);
    }
};
