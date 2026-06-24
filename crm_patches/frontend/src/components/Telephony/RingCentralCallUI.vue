<template>
  <div>
    <div
      v-show="showSmallCallPopup"
      class="ml-2 flex cursor-pointer select-none items-center justify-between gap-1 rounded-full bg-surface-gray-10 px-2 py-[7px] text-base text-ink-gray-2"
      @click="toggleCallPopup"
    >
      <span>{{ phoneNumber }}</span>
      <span>·</span>
      <div>{{ __(callStatus) }}</div>
    </div>
    <div
      v-show="showCallPopup"
      class="fixed bottom-4 right-4 z-20 w-[280px] min-h-32 flex gap-2 flex-col rounded-lg bg-surface-gray-10 p-4 text-ink-gray-2 shadow-2xl"
      @click.stop
    >
      <div class="flex items-center justify-between gap-2">
        <div class="truncate text-base-medium">{{ __('RingCentral') }}</div>
        <Button icon="lucide-x" @click="closeCallPopup" />
      </div>
      <div class="text-sm text-ink-gray-5">{{ phoneNumber }}</div>
      <div class="text-base">{{ __(callStatus) }}</div>
    </div>
  </div>
</template>

<script setup>
import { Button, createResource } from 'frappe-ui'
import { ref } from 'vue'

const phoneNumber = ref('')
const callStatus = ref('Idle')
const showCallPopup = ref(false)
const showSmallCallPopup = ref(false)

function toggleCallPopup() {
  showCallPopup.value = !showCallPopup.value
  showSmallCallPopup.value = !showSmallCallPopup.value
}

function closeCallPopup() {
  showCallPopup.value = false
  showSmallCallPopup.value = false
  callStatus.value = 'Idle'
}

function makeOutgoingCall(number) {
  phoneNumber.value = number
  callStatus.value = 'Calling...'
  showCallPopup.value = true
  showSmallCallPopup.value = false

  createResource({
    url: 'ringcentral_to_erpnext.integrations.crm.make_a_call',
    params: { to_number: phoneNumber.value },
    auto: true,
    onSuccess() {
      callStatus.value = 'Ringing'
    },
    onError(err) {
      callStatus.value = 'Failed'
      console.error(err)
    },
  })
}

function setup() {}

defineExpose({ makeOutgoingCall, setup })
</script>
