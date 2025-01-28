<!-- eslint-disable no-unused-vars -->
<template>
  <q-page class="q-pa-md">
    <div class="q-gutter-md" style="max-width: 300px;padding-left: 30px;">

      <q-input v-model="chartLabel" label="Titre du chart" />

      <q-file type="file" v-model="file" label="Charger un fichier" accept=".csv" @update:model-value="selectFile">
        <template v-slot:prepend>
          <q-icon name="attach_file" />
        </template>
      </q-file>
      <div class="text-body1 q-pt-md" v-if="file">
        L'entète du fichier séléctionner: {{ title }}
      </div>
      <div class="text-body1 q-pt-md" v-if="file">
        Séléctionner le paramètre de l'axe des X
      </div>
      <div v-for="(item, index) in Label" :key="index">
        <q-radio v-model="labels" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="item" :label="item"
          @update:model-value="setLabels" />
      </div>


    </div>
    <div class="row full-width q-px-lg" v-if="fileContent.length > 1" style=" border: 1px solid rgb(231, 226, 226);
        background-color: #f0f0f0;">
      <div class="row">
        <q-btn label="Exporter en pdf" class="q-my-md" @click="exportChart" color="primary" />
      </div>
      <canvas id="chartCanva" style="width: 90vw;height: 400px;" />
    </div>
    <div v-if="fileContent.length < 1 && file">
      <div class="text-h6 text-center">
        Fichier invalide. Le fichier doit avoir deux lignes minimum.
      </div>
    </div>
  </q-page>
</template>

<script setup>
/*eslint-disable no-unused-vars*/
import { onMounted, ref } from 'vue';
import { Chart } from 'chart.js/auto';
import { jsPDF } from "jspdf";


const file = ref(null);
const chartLabel = ref(null);
const title = ref(null);
var chartCanvas = null
var Label = ref([])
var xLabel = []
var fileContent = []
var chartData = []
const labels = ref(null)
//const chartCanva = null
function selectFile() {
  let fr = new FileReader();
  fr.onload = (e) => {
    fileContent = e.target.result.split("\n")
    title.value = fileContent.length > 0 ? fileContent[0] : "Aucune donnée trouvée. Fichier vide"
    Label.value = title.value ? title.value.split(",") : []
    console.log("file content: ", fileContent);

  };
  fr.readAsText(file.value);
}
function initChart() {
  chartCanvas = document.getElementById("chartCanva");
  new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: xLabel,

      datasets: [{
        label: chartLabel.value,
        fill: false,

        lineTension: 0.1,
        backgroundColor: '#812691',
        borderColor: '#21ba45',
        data: chartData,
        borderWidth: 1,
      }]
    }

  })
}

function setLabels(value) {
  xLabel = []; chartData = []
  let valIndex = Label.value.indexOf(value)
  console.log("Label value: ", value, " val index: ", valIndex);
  if (fileContent.length > 0) {
    for (let index = 1; index < fileContent.length; index++) {
      const element = fileContent[index].split(',');
      xLabel.push(element[valIndex])
      let yEl = element.filter(el => el !== element[valIndex])[0]
      chartData.push(Number.parseInt(yEl));
    }

    console.log("chartData: ", chartData, "\nxLabel: ", xLabel);

    initChart()
  }


}
function exportChart() {
  console.log("exporting chart to pdf");
  const chartImg = chartCanvas.toDataURL('image/png');
  const doc = new jsPDF();
  const imgProps = doc.getImageProperties(chartImg);
  const pdfWidth = doc.internal.pageSize.getWidth();
  const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

  doc.addImage(chartImg, 'PNG', 0, 0, pdfWidth, pdfHeight);
  doc.save('chartDoc.pdf');
}
onMounted(e => {
  console.log("app mounted");

})

</script>
