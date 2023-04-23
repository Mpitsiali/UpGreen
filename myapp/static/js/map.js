/*******************************
********** M A P  **************
********************************/

var map = L.map('mapid');
let streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var geojsonData;
fetch(geojsonUrl)
    .then(response => response.json())
    .then(data => {
        geojsonData = L.geoJSON(data, {
            style: getStyle,
            onEachFeature: onEachFeature
        }).addTo(map);

        map.fitBounds(geojsonData.getBounds());
    });

function getStyle() {
    return {
        fillColor: '#00BFFF',
        color: 'black',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    };
}

/*
    * add a hover tooltip to each feature
*/
function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.Value) {
        layer.bindTooltip("Κωδικός OT: " + feature.properties.ot_code + " Όνομα: " + feature.properties.Name);
    }
}


/*******************************
****** M O D A L  **************
********************************/

map.on('click', function (e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    // Use leaflet-pip to pinpoint the GeoJSON feature at the clicked coordinates
    const results = leafletPip.pointInLayer([lng, lat], geojsonData, true);

    if (results.length > 0) {
        const propertyKeysTranslations = {
            "ot_code": "Κωδικός OT",
            "ARITHMOS_O": "Αριθμός ΟΤ",
            "Dimos": "Δήμος",
            "Dim_Enot": "Δημοτική Ενότητα",
            "Name": "Όνομα",
            "ZONE": "Ζώνη",
            "Landuse": "Χρήση γης",
            "dist": "Απόσταση Θάλασσα",
            "dist_tram": "Απόσταση Τραμ",
            "dist_metro": "Απόσταση Μετρό",
            "M_code": "Κωδικός Δήμου",
            "T_K": "Tαχ. Kώδικας",
            "No_of_resi": "Αριθμός Κατοικιών",
            "Sum_of_sqm": "Σύνολο τ.μ.",
            "Avg_sqm_re": "Μέσος όρος τ.μ. κατοικιών",
            "Energy_sco": "Ενεργειακή βαθμολογία",
            "En_Up_cost": "Κόστος ενεργειακής αναβάθμισης",
            "Con_Year_s": "Βαθμολογία έτους κατασκευής",
            "Avg_con_ye": "Μέσος όρος έτους κατασκευής",
            "Block_valu": "Αξία τετραγώνου",
            "Value": "Αντικειμενική Αξία (2021)",
            "Value_q4_2": "Αντικειμενική Αξία Q4",
            "Avg_res_va": "Μέσος όρος αξίας κατοικίας",
            "Ratio": "UpGreen Ratio"
        };

        const euroValues = ['Block_valu','Value','Value_q4_2','Avg_res_va','En_Up_cost']

        const featureProperties = results[0].feature.properties;

        for (const key in propertyKeysTranslations) {
            const modalFieldId = 'modal-' + key;
            const modalElement = document.getElementById(modalFieldId);
            
            if (euroValues.includes(key))
            {
                modalElement.innerHTML = '<strong>' + propertyKeysTranslations[key] + ':</strong> €' + featureProperties[key];

            }
            else if (modalElement) {
                modalElement.innerHTML = '<strong>' + propertyKeysTranslations[key] + ':</strong> ' + featureProperties[key];

            }
        }
        $('#infoModal').modal('show');
    } else {
        console.log("No feature found at the clicked coordinates.");
    }

});

/*******************************
********* L A Y E R S **********
********************************/

function updateLayerColorsBasedOnBuildingAge(geojsData) {
    geojsData.eachLayer(function (layer) {
        const avgBuildingAge = layer.feature.properties.Avg_con_ye;
        let fillColor;

        if (avgBuildingAge > 2000) {
            fillColor = "green";
        } else if (avgBuildingAge > 1980 && avgBuildingAge <= 2000) {
            fillColor = "orange";
        } else if (avgBuildingAge <= 1980) {
            fillColor = "red";
        } else {
            fillColor = "white";
        }

        layer.setStyle({ fillColor: fillColor });
    });
}


function updateLayerColorsBasedOnEnergy(geojsData) {
    geojsData.eachLayer(function (layer) {
        const energyScore = layer.feature.properties.Energy_sco;
        let fillColor;

        if (energyScore > 4) {
            fillColor = "green";
        } else if (energyScore === 4) {
            fillColor = "orange";
        } else if (energyScore < 4) {
            fillColor = "red";
        } else {
            fillColor = "white";
        }

        layer.setStyle({ fillColor: fillColor });
    });
}

function updateLayerColorsBasedOnRatio(geojsData) {
    geojsData.eachLayer(function (layer) {
        const ratio = layer.feature.properties.Ratio;
        let fillColor;

        if (ratio < 0.025) {
            fillColor = "green";
        } else if (ratio < 0.035) {
            fillColor = "orange";
        } else if (ratio >= 0.035) {
            fillColor = "red";
        } else {
            fillColor = "white";
        }

        layer.setStyle({ fillColor: fillColor });
    });
}

function updateLayerColorDefault(geojsData) {
    geojsData.eachLayer(function (layer) {
        layer.setStyle(getStyle(layer.feature));
    });
}


/*******************************
******* B U T T O N S **********
********************************/

document.getElementById('btn-color-0').addEventListener('click', function () {
    updateLayerColorDefault(geojsonData);
});
document.getElementById('btn-color-1').addEventListener('click', function () {
    updateLayerColorsBasedOnBuildingAge(geojsonData);
});

document.getElementById('btn-color-2').addEventListener('click', function () {
    updateLayerColorsBasedOnEnergy(geojsonData);
});

document.getElementById('btn-color-3').addEventListener('click', function () {
    updateLayerColorsBasedOnRatio(geojsonData);
});


/*
    * Add active class to the current button (highlight it)
*/
const buttons = document.querySelectorAll('.custom-btn');

buttons.forEach(button => {
    button.addEventListener('click', (event) => {
        buttons.forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
    });
});


/*
    * Add tooltip to buttons
*/
document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});



