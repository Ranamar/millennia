function setupUnitSelector() {
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

function setupImprovementSelector() {
    let entityList = JSON.parse(this.response);
    let selector = document.getElementById("improvementSelect");
    for (const entity of entityList) {
        let opt = document.createElement("option");
        opt.value = entity;
        //TODO: Get non-ID values back from unit list and put them here.
        //      That's a whole project with figuring out parsing the localization files.
        opt.text = entity;
        selector.add(opt);
    }
}

function setupBuildingSelector() {
    let entityList = JSON.parse(this.response);
    let selector = document.getElementById("buildingSelect");
    for (const entity of entityList) {
        let opt = document.createElement("option");
        opt.value = entity;
        //TODO: Get non-ID values back from unit list and put them here.
        //      That's a whole project with figuring out parsing the localization files.
        opt.text = entity;
        selector.add(opt);
    }
}

const UPGRADE_TREE_URL_BASE = "https://tech-tree-grapher-500188191783.us-central1.run.app"

function setup() {
    let units_req = new XMLHttpRequest();
    units_req.addEventListener("load", setupUnitSelector);
    units_req.open("GET", UPGRADE_TREE_URL_BASE +"/units", true);
    units_req.send();
    let imp_req = new XMLHttpRequest();
    imp_req.addEventListener("load", setupImprovementSelector);
    imp_req.open("GET", UPGRADE_TREE_URL_BASE +"/improvements", true);
    imp_req.send();
    let building_req = new XMLHttpRequest();
    building_req.addEventListener("load", setupBuildingSelector);
    building_req.open("GET", UPGRADE_TREE_URL_BASE +"/buildings", true);
    building_req.send();
}

function updateSelectedUnit() {
    let selector = document.getElementById("unitSelect");
    let unit = selector.value;
    let graph = document.getElementById("graph")
    graph.src = UPGRADE_TREE_URL_BASE + "/unit-upgrade-tree.svg?entity=" + unit
}

function updateSelectedImprovement() {
    let selector = document.getElementById("improvementSelect");
    let improvement = selector.value;
    let graph = document.getElementById("graph")
    graph.src = UPGRADE_TREE_URL_BASE + "/improvement-upgrade-tree.svg?entity=" + improvement
}

function updateSelectedBuilding() {
    let selector = document.getElementById("buildingSelect");
    let building = selector.value;
    let graph = document.getElementById("graph")
    graph.src = UPGRADE_TREE_URL_BASE + "/building-upgrade-tree.svg?entity=" + building
}
