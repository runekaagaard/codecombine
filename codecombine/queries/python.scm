; Function definitions
(function_definition
  name: (identifier) @symbol.name
  body: (block) @symbol.body) @symbol.definition

; Class definitions
(class_definition
  name: (identifier) @symbol.name
  body: (block) @symbol.body) @symbol.definition

; Method definitions (inside classes)
(class_definition
  body: (block 
    (function_definition
      name: (identifier) @symbol.name
      body: (block) @symbol.body) @symbol.definition)) 