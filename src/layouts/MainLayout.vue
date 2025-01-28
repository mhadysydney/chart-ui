<template>
  <q-layout view="lHh Lpr lFf">
    <!--  <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Quasar App
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Essential Links
        </q-item-label>

        <EssentialLink
          v-for="link in linksList"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer> -->

    <q-page-container>
      <router-view />
      <div class="row full-width" style="background-color: #f0f0f0;height: 30px;">
        <div class="col text-caption flex flex-center">
          &copy; 2025 SAT Groupe. All rights reserved. version:1.0.0
        </div>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup>
//import { ref } from 'vue'





</script>
