/***********************************************
* Pop-it menu- © Dynamic Drive (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit http://www.dynamicdrive.com/ for full source code
***********************************************/

var defaultMenuWidth="150px"; //set default menu width.

function getMenuHtml(photo_id, url) {
    menu = '';
    menu += '<a href="#" onclick="a = createXMLHttpRequest(); a.open(\'GET\', \'favorites_action.py?action=mark&photo_id='+photo_id+'\', true); a.send(null);">Mark photo</a>';
    menu += '<a href="#" onclick="a = createXMLHttpRequest(); a.open(\'GET\', \'favorites_action.py?action=delete&photo_id='+photo_id+'\', true); a.send(null);">Remove photo</a>';
    menu += '<a href="'+url+'" target="_blank">Display photo</a>';
    menu += '<br/>';
    menu += '<a href="#">Photo '+photo_id+'</a>';
    return menu;
}

var ie5 = document.all && !window.opera;
var ns6 = document.getElementById;

if (ie5 || ns6) {
    document.write('<div id="popitmenu" onMouseover="clearhidemenu();" onMouseout="dynamichide(event)"></div>');
}

function iecompattest(){
    return (document.compatMode && document.compatMode.indexOf("CSS")!=-1)? document.documentElement : document.body;
}

function showmenu(e, photo_id, optWidth, url) {
    if (!document.all&&!document.getElementById) return;
    clearhidemenu();
    menuobj=ie5? document.all.popitmenu : document.getElementById("popitmenu");
    menuobj.innerHTML = getMenuHtml(photo_id, url);
    menuobj.style.width=(typeof optWidth!="undefined")? optWidth : defaultMenuWidth;
    menuobj.contentwidth=menuobj.offsetWidth;
    menuobj.contentheight=menuobj.offsetHeight;
    eventX=ie5? event.clientX : e.clientX;
    eventY=ie5? event.clientY : e.clientY;
    //Find out how close the mouse is to the corner of the window
    var rightedge=ie5? iecompattest().clientWidth-eventX : window.innerWidth-eventX;
    var bottomedge=ie5? iecompattest().clientHeight-eventY : window.innerHeight-eventY;
    //if the horizontal distance isn't enough to accomodate the width of the context menu
    if (rightedge<menuobj.contentwidth) {
        //move the horizontal position of the menu to the left by it's width
        menuobj.style.left=ie5? iecompattest().scrollLeft+eventX-menuobj.contentwidth+"px" : window.pageXOffset+eventX-menuobj.contentwidth+"px";
    } else {
        //position the horizontal position of the menu where the mouse was clicked
        menuobj.style.left=ie5? iecompattest().scrollLeft+eventX+"px" : window.pageXOffset+eventX+"px";
    }

    //same concept with the vertical position
    if (bottomedge<menuobj.contentheight) {
        menuobj.style.top=ie5? iecompattest().scrollTop+eventY-menuobj.contentheight+"px" : window.pageYOffset+eventY-menuobj.contentheight+"px";
    } else {
        menuobj.style.top=ie5? iecompattest().scrollTop+event.clientY+"px" : window.pageYOffset+eventY+"px";
    }
    menuobj.style.visibility = "visible";
    return false;
}

function contains_ns6(a, b) {
    //Determines if 1 element in contained in another- by Brainjar.com
    while (b.parentNode) {
        if ((b = b.parentNode) == a) {
            return true;
        }
    }
    return false;
}

function hidemenu(){
    if (window.menuobj) {
        menuobj.style.visibility="hidden";
    }
}

function dynamichide(e) {
    if (ie5&&!menuobj.contains(e.toElement)) {
        hidemenu();
    } else if (ns6&&e.currentTarget!= e.relatedTarget&& !contains_ns6(e.currentTarget, e.relatedTarget)) {
        hidemenu();
    }
}

function delayhidemenu() {
    delayhide = setTimeout("hidemenu()",500);
}

function clearhidemenu() {
    if (window.delayhide) {
        clearTimeout(delayhide);
    }
}

if (ie5||ns6) {
    document.onclick=hidemenu;
}

