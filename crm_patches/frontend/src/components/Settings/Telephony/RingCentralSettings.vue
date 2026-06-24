<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex gap-1 items-center">
        <Button
          variant="ghost"
          icon-left="lucide-chevron-left"
          :label="__('RingCentral Settings')"
          size="md"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 text-2xl-semibold hover:opacity-70 !pr-0 !max-w-96 !justify-start"
          @click="emit('updateStep', 'telephony-settings')"
        />
      </div>
    </template>
    <template #content>
      <div v-if="settings.loading" class="text-p-sm text-ink-gray-6">
        {{ __('Loading...') }}
      </div>
      <div v-else class="space-y-6">
        <div class="flex items-center justify-between gap-8">
          <div class="flex flex-col">
            <div class="text-p-base-medium text-ink-gray-7">
              {{ __('Integration Status') }}
            </div>
            <div class="text-p-sm text-ink-gray-5">
              {{
                __(
                  'RingCentral credentials and webhooks are managed in Frappe Desk.',
                )
              }}
            </div>
          </div>
          <Badge
            :label="settings.data?.enabled ? __('Enabled') : __('Disabled')"
            :theme="settings.data?.enabled ? 'green' : 'gray'"
            variant="subtle"
          />
        </div>

        <div
          v-if="settings.data?.enabled"
          class="rounded-lg border border-outline-elevation-2 p-4 space-y-2"
        >
          <div class="text-p-sm text-ink-gray-6">
            {{ __('Client ID') }}: {{ settings.data?.client_id || '—' }}
          </div>
          <div class="text-p-sm text-ink-gray-6">
            {{ __('Sandbox') }}:
            {{ settings.data?.use_sandbox ? __('Yes') : __('No') }}
          </div>
        </div>

        <div class="space-y-3">
          <Button
            variant="solid"
            :label="__('Open RingCentral Settings in Desk')"
            @click="openDeskSettings"
          />
          <Button
            variant="subtle"
            :label="__('Manage RingCentral Agents in Desk')"
            @click="openDeskAgents"
          />
        </div>

        <div class="text-p-sm text-ink-gray-5">
          {{
            __(
              'Each sales rep needs a RingCentral Agent record with their RC extension ID and direct number before click-to-call will work.',
            )
          }}
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
</template>

<script setup>
import { Badge, Button, createResource } from 'frappe-ui'

const emit = defineEmits(['updateStep'])

const settings = createResource({
  url: 'ringcentral_to_erpnext.api.ringcentral.get_settings',
  auto: true,
})

function openDeskSettings() {
  window.open('/app/ringcentral-settings', '_blank')
}

function openDeskAgents() {
  window.open('/app/ringcentral-agent', '_blank')
}
</script>
