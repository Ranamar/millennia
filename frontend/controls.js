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

function setupTerrainSelector() {
    let terrainReqList = JSON.parse(this.response);
    let selector = document.getElementById("terrainSelect");
    for (const entity of terrainReqList) {
        let opt = document.createElement("option");
        opt.value = entity;
        //TODO: Get non-ID values back from unit list and put them here.
        //      That might be doable from localization files, or we might need to special-case it somehow.
        opt.text = entity;
        selector.add(opt);
    }
}

const BACKEND_URL_BASE = "https://tech-tree-grapher-500188191783.us-central1.run.app"

function setup() {
    let units_req = new XMLHttpRequest();
    units_req.addEventListener("load", setupUnitSelector);
    units_req.open("GET", BACKEND_URL_BASE +"/units", true);
    units_req.send();
    let imp_req = new XMLHttpRequest();
    imp_req.addEventListener("load", setupImprovementSelector);
    imp_req.open("GET", BACKEND_URL_BASE +"/improvements", true);
    imp_req.send();
    let building_req = new XMLHttpRequest();
    building_req.addEventListener("load", setupBuildingSelector);
    building_req.open("GET", BACKEND_URL_BASE +"/buildings", true);
    building_req.send();

    let terrain_req = new XMLHttpRequest();
    terrain_req.addEventListener("load", setupTerrainSelector);
    terrain_req.open("GET", BACKEND_URL_BASE +"/terrains", true);
    terrain_req.send();
}

function updateSelectedUnit() {
    let selector = document.getElementById("unitSelect");
    let unit = selector.value;
    let graph = document.getElementById("graph")
    graph.src = BACKEND_URL_BASE + "/unit-upgrade-tree.svg?entity=" + unit
    clearImprovementSelector();
    clearBuildingSelector();
    clearTerrainSelector()
}

function clearUnitSelector() {
    let selector = document.getElementById("unitSelect");
    selector.value = ""
}

function updateSelectedImprovement() {
    let selector = document.getElementById("improvementSelect");
    let improvement = selector.value;
    let graph = document.getElementById("graph")
    graph.src = BACKEND_URL_BASE + "/improvement-upgrade-tree.svg?entity=" + improvement
    clearUnitSelector();
    clearBuildingSelector();
    clearTerrainSelector()
}

function clearImprovementSelector() {
    let selector = document.getElementById("improvementSelect");
    selector.value = ""
}

function updateSelectedBuilding() {
    let selector = document.getElementById("buildingSelect");
    let building = selector.value;
    let graph = document.getElementById("graph")
    graph.src = BACKEND_URL_BASE + "/building-upgrade-tree.svg?entity=" + building
    clearImprovementSelector();
    clearUnitSelector();
    clearTerrainSelector()
}

function clearBuildingSelector() {
    let selector = document.getElementById("buildingSelect");
    selector.value = ""
}


function updateSelectedTerrain() {
    let selector = document.getElementById("terrainSelect");
    // Because of the way that we jammed stuff into the selector, this value is a single string with comma-separated values.
    let terrain = selector.value;
    let graph = document.getElementById("graph")
    console.log(terrain)
    graph.src = BACKEND_URL_BASE + "/upgrades-by-terrain.svg?requirements=" + terrain
    clearImprovementSelector();
    clearBuildingSelector();
    clearUnitSelector();
}

function clearTerrainSelector() {
    let selector = document.getElementById("terrainSelect");
    selector.value = ""
}