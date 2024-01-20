var util = require("util");
var httpclient;
var PythonshellNode = require('./qnn0');

module.exports = function(RED) {
  "use strict";

  function PythonshellInNode(n) {
    RED.nodes.createNode(this,n);

    var node = this;
    node.config = n; // copy config to the backend so that down bellow we can have a reference

    var pyNode = new PythonshellNode(n);

    pyNode.setStatusCallback(node.status.bind(node))
  
    node.on("input",function(msg) {
      pyNode.onInput(msg, function(result){
        node.send(result);
      }, function(err){
        node.error(err);
      });
    });

    node.on('close', ()=>pyNode.onClose());
  }

  RED.nodes.registerType("qnn", PythonshellInNode);

  RED.httpAdmin.post("/pythonshell/:id", RED.auth.needsPermission("pythonshell.query"), function(req,res) {
    var node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        if (node.config.continuous){// see above comment
          node.receive({payload: 'pythonshell@close'})
        } else {
          node.receive();
        }
        res.sendStatus(200);
      } catch(err) {
          res.sendStatus(500);
          node.error(RED._("pythonshell.failed",{error:err.toString()}));
      }
    } else {
        res.sendStatus(404);
    }
  });

}
