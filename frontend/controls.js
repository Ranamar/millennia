function setup_unit_selector() {
    let unitList = JSON.parse(this.response);
    let selector = document.getElementById("unitSelect");
    for (const unit of unitList) {
        let opt = document.createElement("option");
        opt.value = unit;
        //TODO: Get non-ID values back from unit list and put them here.
        //      That's a whole project with figuring out parsing the localization files.
        opt.text = unit;
        selector.add(opt);
    }
}

const UPGRADE_TREE_URL_BASE = "https://tech-tree-grapher-500188191783.us-central1.run.app"

function setup() {
    let units_req = new XMLHttpRequest();
    units_req.addEventListener("load", setup_unit_selector);
    units_req.open("GET", UPGRADE_TREE_URL_BASE +"/units", true);
    units_req.send();
}

function updateSelectedUnit() {
    let selector = document.getElementById("unitSelect");
    let unit = selector.value;
    let graph = document.getElementById("graph")
    graph.src = UPGRADE_TREE_URL_BASE + "/upgrade_tree.svg?entity=" + unit
}