<template>
	<FormShell :title="__('Bulk assign learners')" size="xl" @close="close">
		<template #default>
			<div v-if="!isAdmin" class="p-4 text-ink-gray-6">
				{{ __('Only administrators can assign courses.') }}
			</div>
			<div v-else class="space-y-5">
				<div>
					<label class="mb-1 block text-p-sm font-medium">{{ __('Client organization') }}</label>
					<select v-model="organization" class="w-full rounded border border-outline-gray-2 bg-white p-3 text-p-sm" @change="preview = null">
						<option value="">{{ __('Whitehouse direct training (no organization)') }}</option>
						<option v-for="item in organizations" :key="item.name" :value="item.name" :disabled="item.status !== 'Active'">{{ item.organization_name }}</option>
					</select>
				</div>
				<p class="text-p-sm text-ink-gray-7">
					{{ __('Upload a UTF-8 CSV with an email column. Optional columns: first_name, last_name. Maximum 500 learners. Preview validates every row before anything is changed.') }}
				</p>
				<input
					type="file"
					accept=".csv,text/csv"
					class="block w-full rounded border border-outline-gray-2 p-3 text-p-sm"
					@change="readFile"
				/>
				<FormControl
					v-model="createMissing"
					type="checkbox"
					:label="__('Create missing learner accounts')"
				/>
				<p v-if="createMissing" class="text-p-xs text-ink-gray-6">
					{{ __('New learners receive the standard account welcome email. Existing users and roles are never changed.') }}
				</p>
				<div v-if="preview" class="rounded border border-outline-gray-2 p-4 text-p-sm">
					<p class="font-medium text-ink-gray-9">
						{{ __('{0} rows · {1} new accounts · {2} assignments · {3} already assigned').format(preview.rows, preview.new_users, preview.to_assign, preview.already_assigned) }}
					</p>
					<p v-if="preview.applied" class="mt-2 text-green-700">
						{{ __('Import complete.') }}
					</p>
					<ul v-if="preview.errors?.length" class="mt-3 list-disc ps-5 text-red-700">
						<li v-for="error in preview.errors" :key="error.row">
							{{ __('Row {0}: {1}').format(error.row, error.message) }}
						</li>
					</ul>
				</div>
			</div>
		</template>
		<template #actions>
			<div v-if="isAdmin" class="flex justify-end gap-2">
				<HeaderButton
					:label="__('Preview')"
					variant="outline"
					:loading="busy"
					:disabled="!csvText"
					@click="submit(true)"
				/>
				<HeaderButton
					:label="__('Import and assign')"
					variant="solid"
					:loading="busy"
					:disabled="!preview?.ok || preview?.applied"
					@click="submit(false)"
				/>
			</div>
		</template>
	</FormShell>
</template>

<script setup lang="ts">
import { call, FormControl, getCachedListResource, toast } from 'frappe-ui'
import { computed, inject, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import FormShell from '@/components/FormShell.vue'
import HeaderButton from '@/components/HeaderButton.vue'
import { useFormRoute } from '@/composables/useFormRoute'
import type { SessionUser } from '@/types'

type ImportResult = {
	ok: boolean
	rows: number
	new_users: number
	to_assign: number
	already_assigned: number
	errors: { row: number; message: string }[]
	applied: boolean
}

const props = defineProps<{ courseName: string }>()
const route = useRoute()
const user = inject<SessionUser>('$user')!
const isAdmin = computed(() => !!(user.data?.is_moderator || user.data?.is_system_manager))
const parent = {
	name: 'CourseDetail',
	params: { courseName: props.courseName },
	hash: route.hash || '#dashboard',
}
const { close } = useFormRoute(parent)
const csvText = ref('')
const createMissing = ref(false)
const preview = ref<ImportResult | null>(null)
const busy = ref(false)
const organization = ref('')
const organizations = ref<{ name: string; organization_name: string; status: string }[]>([])

onMounted(async () => {
	if (isAdmin.value) organizations.value = await call('lms.lms.admin_learning.get_organizations')
})

async function readFile(event: Event) {
	const file = (event.target as HTMLInputElement).files?.[0]
	preview.value = null
	csvText.value = ''
	if (!file) return
	if (file.size > 100_000) {
		toast.error(__('CSV must be smaller than 100 KB.'))
		return
	}
	csvText.value = await file.text()
}

async function submit(dryRun: boolean) {
	if (!isAdmin.value || !csvText.value || busy.value) return
	busy.value = true
	try {
		preview.value = await call('lms.lms.admin_learning.bulk_assign_course', {
			course: props.courseName,
			csv_text: csvText.value,
			create_missing: createMissing.value ? 1 : 0,
			organization: organization.value || null,
			dry_run: dryRun ? 1 : 0,
		}) as ImportResult
		if (preview.value.applied) {
			getCachedListResource(['courseProgress', props.courseName])?.reload()
			toast.success(__('Learners assigned successfully'))
		}
	} catch (error: any) {
		toast.error(error?.messages?.[0] || __('Unable to import learners'))
	} finally {
		busy.value = false
	}
}
</script>
