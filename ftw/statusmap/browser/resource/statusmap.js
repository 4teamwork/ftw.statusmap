var statusmap = new Object();

statusmap.toggleCheckboxes = function(el){
    var status;
    el.checked ? status = 1 : status = 0;
    var boxes = jQuery(".statusmap-uids");
    for(var i=0; i<boxes.length; i++) {
        if(boxes[i].disabled) {
            continue;
        }
        if(status) {
            boxes[i].checked = true;
            boxes[i].setAttribute('checked','checked');
        } else {
            boxes[i].checked = false;
            boxes[i].removeAttribute('checked');
        }
    }
};

statusmap.selectTransition = function(el) {
    var select_all = jQuery('#select_all')[0];
    select_all.disabled = false;
    select_all.removeAttribute('disabled');
    var transition = el.getAttribute('value');
    //
    var boxes = jQuery('.statusmap-uids');
    for(var i=0; i<boxes.length; i++) {
        var node = boxes[i];
        var id = node.id.substr('item-'.length);
        node.disabled = true;
        node.setAttribute('disabled', 'disabled');
        var object_transitions = possible_transitions[id];
        for(var t=0; t<object_transitions.length; t++) {
            if(transition==object_transitions[t]) {
                node.disabled = false;
                node.removeAttribute('disabled');
            }
        }
        if(node.disabled) {
            node.checked = false;
            node.removeAttribute('checked');
        }
    }
};
