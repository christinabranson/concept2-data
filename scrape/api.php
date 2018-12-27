<?php

$json = json_decode(file_get_contents('php://input'));
echo print_r($json, true);
error_log(print_r($json, true));
mail("clbranson@gmail.com", "Concept2 json data",print_r($json, true));