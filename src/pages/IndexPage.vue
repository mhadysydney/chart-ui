<!-- eslint-disable no-unused-vars -->
<template>
  <q-page class="q-pa-md">
    <div class="q-gutter-md" style="max-width: 300px; padding-left: 30px">
      <q-btn
        label="Ajouter un nouveau graphe"
        @click="newCanvas"
        icon="add"
        v-if="chartCanvas.length > 0"
      />
      <div class="row no-wrap scroll-x full-width q-pa-md" style="max-height: 300px">
        <q-card v-for="n in chartCanvas" :key="n" class="col-auto">
          <q-card-section>
            <q-input v-model="chartLabel" label="En tête du graphe" />

            <q-file
              type="file"
              v-model="files"
              use-chips
              multiple
              label="Charger un fichier"
              accept=".csv"
              @update:model-value="selectFile"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </q-card-section>
        </q-card>

        <q-card v-for="(file, n) in files" :key="n">
          <q-card-section>
            <div class="text-body1 q-pt-md">Propriétés du fichier {{ file.name }}</div>
            <div v-for="(item, index) in Label" :key="index">
              <div class="text-body1 q-pt-md" v-if="files">
                Séléctionner le paramètre de l'axe des X
              </div>
              <q-radio
                v-model="labels"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                :val="item"
                :label="item"
                @update:model-value="setLabels"
              />
            </div>
            <div class="q-gutter-md">
              <q-input v-model="chartLabel1" label="Titre du graphe" />
              <div class="text-body1 q-pt-md" v-if="files">Séléctionner le type de graphe</div>
              <q-radio
                v-model="chartType"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="line"
                label="Courbe"
              />
              <q-radio
                v-model="chartType"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="histo"
                label="Histogramme"
              />
              <q-radio
                v-model="chartType"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="doghnut"
                label="Circulaire"
              />
              <div class="text-body1 q-pt-md" v-if="files">Séléctionner la couleur du graphe</div>
              <q-input filled v-model="color">
                <template v-slot:append>
                  <q-icon name="colorize" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-color v-model="chartColor" />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
    <div
      class="row full-width q-px-lg"
      v-for="nCanva in chartCanvas"
      :key="nCanva"
      style="border: 1px solid rgb(231, 226, 226); background-color: #f0f0f0"
    >
      <div class="row">
        <q-btn
          label="Exporter en pdf"
          class="q-my-md"
          @click="exportChart(nCanva)"
          color="primary"
        />
      </div>
      <canvas :id="`chartCanva_${nCanva}`" style="width: 90vw; height: 400px" />
    </div>
    <div v-if="fileContent.length < 1 && files.length < 1">
      <div class="text-h6 text-center">
        Fichier invalide. Le fichier doit avoir deux lignes minimum.
      </div>
    </div>
  </q-page>
</template>

<script>
//import { onMounted, ref } from 'vue'
import { Chart } from 'chart.js/auto'
import { jsPDF } from 'jspdf'

export default {
  data() {
    return {
      files: [],
      chartLabel: null,
      title: null,
      chartCanvas: [1],
      Label: [],
      xLabels: [],
      fileContent: [],
      chartData: [],
      labels: null,
      chartType: 'line',
      chartColor: null,
      chartLabel1: null,
    }
  },

  methods: {
    newCanvas() {
      this.chartCanvas.push(this.chartCanvas.length + 1)
      console.log('new chart added: ', this.chartCanvas)
    },
    selectFile() {
      for (const file of this.files) {
        let fr = new FileReader()
        fr.onload = (e) => {
          this.fileContent = e.target.result.split('\n')
          this.title =
            this.fileContent.length > 0
              ? this.fileContent[0]
              : 'Aucune donnée trouvée. Fichier vide'
          this.Label = this.title ? this.title.split(',') : []
          console.log('file content: ', this.fileContent)
        }
        fr.readAsText(file)
      }
      //if(this.files.length>=1)
    },
    initChart() {
      this.chartCanvas = document.getElementById('chartCanva')
      new Chart(this.chartCanvas, {
        type: 'line',
        data: {
          labels: this.xLabels,

          datasets: [
            {
              label: this.chartLabel,
              fill: false,

              lineTension: 0.1,
              backgroundColor: '#812691',
              borderColor: '#21ba45',
              data: this.chartData,
              borderWidth: 1,
            },
          ],
        },
      })
    },

    setLabels(value) {
      this.xLabels = []
      this.chartData = []
      let valIndex = this.Label.indexOf(value)
      console.log('Label value: ', value, ' val index: ', valIndex)
      if (this.fileContent.length > 0) {
        for (let index = 1; index < this.fileContent.length; index++) {
          const element = this.fileContent[index].split(',')
          this.xLabels.push(element[valIndex])
          let yEl = element.filter((el) => el !== element[valIndex])[0]
          this.chartData.push(Number.parseInt(yEl))
        }

        console.log('chartData: ', this.chartData, '\nxLabel: ', this.xLabels)

        this.initChart()
      }
    },
    exportChart() {
      console.log('exporting chart to pdf')
      const chartImg = this.chartCanvas.toDataURL('image/png')
      const doc = new jsPDF()
      const imgProps = doc.getImageProperties(chartImg)
      const pdfWidth = doc.internal.pageSize.getWidth()
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width

      doc.addImage(chartImg, 'PNG', 0, 0, pdfWidth, pdfHeight)
      doc.save('chartDoc.pdf')
    },
  },
  mounted() {
    console.log('App mounted')
  },
}
</script>
