<!-- eslint-disable no-unused-vars -->
<template>
  <q-page class="q-pa-md">
    <div class="row items-center" style="max-width: 300px; padding-left: 30px">
      <q-btn
        label="Ajouter un nouveau conteneur"
        @click="newCanvas"
        icon="add"
        class="q-ml-md"
        v-if="chartCanvas.length > 0"
      />
      <q-btn
        label="Exporter tous les conteneurs"
        @click="exportAll"
        icon="file_export"
        color="primary"
        class="q-ml-md"
        v-if="chartCanvas.length > 0 && chartContainer.length > 1"
      />
      <q-btn
        label="Reinitialiser tout"
        @click="reset"
        icon="file_export"
        color="primary"
        class="q-ml-md"
        v-if="chartCanvas.length > 0 && chartContainer.length > 1"
      />
    </div>
    <div class="row full-width">
      <div class="row no-wrap scroll-x full-width q-pa-md" style="height: auto">
        <q-card v-for="n in chartContainer" :key="n" class="col-auto">
          <q-card-section>
            <q-input v-model="chartLabel[n]" label="En tête du graphe" />

            <q-file
              type="file"
              v-model="files"
              use-chips
              multiple
              label="Charger vos fichiers"
              accept=".csv"
              @update:model-value="selectFile"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </q-card-section>

          <div v-if="files.length > 0">
            <q-separator color="black" inset />
            <q-card-section>
              <div class="text-body1 q-pt-xs">
                Voulez-vous ajouter les données des fichiers dans un meme conteneur ou créer un
                conteneur pour chaque fichier?
              </div>
              <q-radio
                v-model="combineChart[n]"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="0"
                label="Meme conteneur"
                @update:model-value="setCombine(n)"
              />
              <q-radio
                v-model="combineChart[n]"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="1"
                label="Conteneur séparé"
                @update:model-value="setCombine(n)"
              />
            </q-card-section>
            <q-separator color="black" inset />
            <q-card-section>
              <q-btn
                label="Générer le graphe"
                class="q-my-md"
                @click="initChart(n)"
                color="primary"
              />
            </q-card-section>
          </div>
        </q-card>

        <q-card v-for="(file, n) in files" :key="n" class="q-ml-md">
          <q-card-section>
            <div class="text-h6 q-pt-md">Propriétés du fichier {{ file.name }}</div>
            <div class="text-body1 q-pt-xs" v-if="files">
              Séléctionner le paramètre de l'axe des X
            </div>
            <div class="q-gutter-md">
              <!-- <template v-for="(items, index) in Labels[n]" :key="index"> -->
              <q-radio
                v-for="(item, index) in Labels[n]"
                :key="index"
                v-model="labels"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                :val="item"
                :label="item"
                @update:model-value="setLabels(item, n)"
              />
              <!--  </template> -->
            </div>
          </q-card-section>
          <q-separator color="black" inset />
          <q-card-section>
            <div class="q-gutter-md">
              <q-input v-model="chartsLabels[n]" filled label="Titre du graphe" />
              <div class="text-body1 q-pt-xs" v-if="files">Séléctionner le type de graphe</div>
              <q-radio
                v-model="chartType[n]"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="line"
                label="Courbe"
              />
              <q-radio
                v-model="chartType[n]"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="bar"
                label="Histogramme"
              />
              <q-radio
                v-model="chartType[n]"
                checked-icon="task_alt"
                unchecked-icon="panorama_fish_eye"
                val="doughnut"
                label="Circulaire"
              />
            </div>
          </q-card-section>
          <q-separator color="black" inset />
          <q-card-section>
            <div class="text-body1 q-pt-xs" v-if="files">Séléctionner la couleur du graphe</div>
            <q-input filled v-model="chartColors[n]">
              <template v-slot:append>
                <q-icon name="colorize" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-color v-model="chartColors[n]" />
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
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
      <div class="row full-width">
        <div class="col">
          <q-btn
            label="Exporter en pdf"
            class="q-my-md"
            @click="exportChart(nCanva)"
            color="primary"
            icon="download_for_offline"
          />
        </div>
        <div class="col">
          <q-btn
            class="q-my-md float-right shadow-23"
            @click="removeChart(nCanva)"
            color="red"
            round
            icon="close"
          />
        </div>
      </div>
      <canvas :id="`chartCanva_${nCanva}`" style="width: 90vw; height: 400px" />
    </div>
    <div v-if="checkFiles && fileContent.length < 1 && files.length < 1">
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
import { document } from 'postcss'

export default {
  data() {
    return {
      files: [],
      chartLabel: [1],
      title: null,
      combineChart: ['0'],
      chartContainer: [1],
      chartCanvas: [],
      Labels: [],
      xLabels: [],
      fileContent: [],
      chartsData: [],
      labels: [],
      chartType: 'line',
      chartColors: null,
      chartsLabels: null,
      checkFiles: false,
      tmpLabels: [1],
    }
  },

  methods: {
    newCanvas() {
      this.chartCanvas.push(this.chartCanvas.length + 1)
      console.log('new chart added: ', this.chartCanvas)
    },
    removeChart(id) {
      let canvas = document.getElementById('chartCanva_' + id)
      if (canvas) console.log('canvas to remove: chartCanva_', id)
    },
    initVars() {
      console.log('init vars')

      this.Labels = Array(this.files.length)
      this.xLabels = Array(this.files.length)
      this.chartColors = Array(this.files.length)
      this.chartsLabels = Array(this.files.length)
      this.chartType = Array(this.files.length)
      this.chartsData = Array(this.files.length)
      this.fileContent = Array(this.files.length)
    },
    reset() {
      let x = confirm('Voulez-vous tout effacer?')
      if (x) location.reload()
    },
    setCombine(ind) {
      let combine = this.combineChart[ind]
      console.log('combine: ', combine)
      if (this.tmpLabels[ind].length == 0) this.tmpLabels[ind] = this.Labels
      if (combine === '0') {
        console.log('Labelde : ', ind, ': ', this.Labels[ind])
        this.Labels = this.Labels[0]
      } else {
        this.Labels = this.tmpLabels[ind]
      }
    },
    selectFile() {
      this.initVars()
      for (const [index, file] of this.files.entries()) {
        console.log('file index: ', index)

        let fr = new FileReader()
        fr.onload = (e) => {
          this.fileContent[index] = e.target.result.split('\n')
          this.title =
            this.fileContent[index].length > 0
              ? this.fileContent[index][0]
              : 'Aucune donnée trouvée. Fichier vide'
          this.Labels[index] = this.title ? this.title.split(',') : []
          console.log(`Labels[${index}]: ${this.Labels[index]}`)
        }
        fr.readAsText(file)
      }
      //if(this.files.length>=1)
    },
    initChart(id = 0) {
      this.chartCanvas = document.getElementById('chartCanva_' + id)
      new Chart(this.chartCanvas, {
        type: this.chartType[id],
        options: {
          plugins: {
            title: this.chartLabel[id],
          },
        },
        data: {
          labels: this.xLabels[id],

          datasets: [
            {
              label: this.chartsLabels[id],
              fill: false,
              lineTension: 0.4,
              backgroundColor: this.chartColors[id],
              borderColor: this.chartColors[id],
              data: this.chartData[id],
              borderWidth: 1,
            },
          ],
        },
      })
    },

    setLabels(value, index) {
      this.xLabels[index] = []
      this.chartsData[index] = []
      let valIndex = this.Labels[index].indexOf(value)
      console.log('Label value: ', value, ' val index: ', valIndex)
      //if (this.fileContent.length > 0) {
      for (let i = 0; i < this.files.length; i++)
        for (let index = 1; index < this.fileContent[i].length; index++) {
          const element = this.fileContent[index].split(',')
          this.xLabels[index].push(element[valIndex])
          let yEl = element.filter((el) => el !== element[valIndex])[0]
          this.chartData[index].push(Number.parseInt(yEl))
        }

      console.log('chartData: ', this.chartData, '\nxLabel: ', this.xLabels)

      //this.initChart()
      //}
    },
    exportChart(id) {
      console.log('exporting chart to pdf')
      const chartImg = this.chartCanvas[id].toDataURL('image/png')
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
