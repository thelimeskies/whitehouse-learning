<template>
	<div class="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
		<div
			v-if="!isAdmin"
			class="rounded-2xl border border-outline-gray-2 p-8 text-ink-gray-6"
		>
			{{ __('Only Whitehouse administrators can manage training clients.') }}
		</div>
		<template v-else>
			<router-link
				:to="{ name: 'Clients' }"
				class="text-sm font-medium text-ink-blue-6 hover:underline"
				>← {{ __('Clients & people') }}</router-link
			>
			<div
				v-if="workspace.loading && !workspace.data"
				class="mt-8 text-sm text-ink-gray-6"
			>
				{{ __('Loading client workspace…') }}
			</div>
			<div
				v-else-if="workspace.error || !workspace.data"
				class="mt-8 rounded-2xl border border-outline-gray-2 p-8 text-ink-gray-6"
			>
				{{ __('This client could not be loaded.') }}
				<button
					type="button"
					class="ms-2 font-medium text-ink-blue-6"
					@click="workspace.fetch()"
				>
					{{ __('Try again') }}
				</button>
			</div>
			<template v-else>
				<header class="mt-5 flex flex-wrap items-start justify-between gap-4">
					<div>
						<p
							class="text-xs font-semibold uppercase tracking-widest text-ink-blue-6"
						>
							{{ __('Client workspace') }}
						</p>
						<h1 class="mt-2 text-3xl font-semibold text-ink-gray-9">
							{{ workspace.data.organization.organization_name }}
						</h1>
						<p class="mt-2 text-sm text-ink-gray-6">
							{{
								__(
									'Whitehouse owns the accounts and training. This client does not have a separate admin portal.',
								)
							}}
						</p>
					</div>
					<router-link
						:to="{
							name: 'Statistics',
							query: { organization: props.organization },
						}"
						class="rounded-lg border border-outline-gray-2 bg-surface-elevation-1 px-4 py-2.5 text-sm font-medium text-ink-gray-8 hover:bg-surface-gray-2"
						>{{ __('View outcomes') }} →</router-link
					>
				</header>
				<div class="mt-7 grid gap-4 sm:grid-cols-3">
					<div
						class="rounded-xl border border-outline-gray-2 bg-surface-elevation-1 p-5"
					>
						<p class="text-xs uppercase tracking-wide text-ink-gray-5">
							{{ __('Status') }}
						</p>
						<p class="mt-2 text-xl font-semibold text-ink-gray-9">
							{{ workspace.data.organization.status }}
						</p>
					</div>
					<div
						class="rounded-xl border border-outline-gray-2 bg-surface-elevation-1 p-5"
					>
						<p class="text-xs uppercase tracking-wide text-ink-gray-5">
							{{ __('Learners') }}
						</p>
						<p class="mt-2 text-xl font-semibold text-ink-gray-9">
							{{ workspace.data.learner_count }}
						</p>
					</div>
					<div
						class="rounded-xl border border-outline-gray-2 bg-surface-elevation-1 p-5"
					>
						<p class="text-xs uppercase tracking-wide text-ink-gray-5">
							{{ __('Course assignments') }}
						</p>
						<p class="mt-2 text-xl font-semibold text-ink-gray-9">
							{{ workspace.data.assignment_count }}
						</p>
					</div>
				</div>

				<div
					class="mt-7 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.25fr)]"
				>
					<section
						class="h-fit rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-6"
					>
						<div
							class="flex size-9 items-center justify-center rounded-lg bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
						>
							1
						</div>
						<h2 class="mt-4 text-xl font-semibold text-ink-gray-9">
							{{ __('Client profile') }}
						</h2>
						<p class="mt-1 text-sm text-ink-gray-6">
							{{
								__(
									'Record who Whitehouse coordinates with and what the training is meant to achieve.',
								)
							}}
						</p>
						<form class="mt-5 space-y-3" @submit.prevent="saveProfile">
							<label
								for="client-contact"
								class="block text-sm font-medium text-ink-gray-8"
								>{{ __('Primary contact email') }}</label
							>
							<input
								id="client-contact"
								v-model="contactEmail"
								type="email"
								autocomplete="email"
								:placeholder="__('contact@client.com')"
								class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							<label
								for="client-brief"
								class="block text-sm font-medium text-ink-gray-8"
								>{{ __('Internal training brief') }}</label
							>
							<textarea
								id="client-brief"
								v-model="notes"
								rows="4"
								maxlength="2000"
								:placeholder="__('Goals, audience, delivery notes…')"
								class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							<p v-if="profileError" role="alert" class="text-sm text-red-600">
								{{ profileError }}
							</p>
							<button
								type="submit"
								:disabled="savingProfile"
								class="rounded-lg border border-outline-gray-2 px-4 py-2.5 text-sm font-medium text-ink-gray-9 hover:bg-surface-gray-2 disabled:opacity-50"
							>
								{{ savingProfile ? __('Saving…') : __('Save profile') }}
							</button>
						</form>
					</section>

					<section
						class="rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-6"
					>
						<div
							class="flex size-9 items-center justify-center rounded-lg bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
						>
							2
						</div>
						<h2 class="mt-4 text-xl font-semibold text-ink-gray-9">
							{{ __('Assign training') }}
						</h2>
						<p class="mt-1 text-sm leading-6 text-ink-gray-6">
							{{
								__(
									'Choose a course, then add one learner or import a roster. Whitehouse creates new learner accounts and reuses existing ones.',
								)
							}}
						</p>
						<div
							v-if="workspace.data.organization.status !== 'Active'"
							class="mt-4 rounded-lg bg-surface-amber-2 p-3 text-sm text-ink-gray-8"
						>
							{{
								__(
									'This client is paused. Activate it from Clients & people before making new assignments.',
								)
							}}
						</div>
						<div
							v-if="!workspace.data.courses.length"
							class="mt-4 rounded-lg bg-surface-gray-1 p-3 text-sm text-ink-gray-7"
						>
							{{
								__(
									'No published courses yet. Publish a course before onboarding learners.',
								)
							}}
						</div>
						<template v-else>
							<label
								for="client-course"
								class="mt-5 block text-sm font-medium text-ink-gray-8"
								>{{ __('Training course') }}</label
							>
							<select
								id="client-course"
								v-model="course"
								class="mt-1.5 w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9"
								@change="preview = null"
							>
								<option value="">{{ __('Choose a course') }}</option>
								<option
									v-for="item in workspace.data.courses"
									:key="item.name"
									:value="item.name"
								>
									{{ item.title }}
								</option>
							</select>
							<div class="mt-6 border-t border-outline-gray-2 pt-5">
								<h3 class="font-semibold text-ink-gray-9">
									{{ __('Add one learner') }}
								</h3>
								<p class="mt-1 text-sm text-ink-gray-6">
									{{
										__(
											'For an existing user, only their email is needed. Enter a name to invite a new user.',
										)
									}}
								</p>
								<form
									class="mt-4 grid gap-3 sm:grid-cols-2"
									@submit.prevent="assignOne"
								>
									<div class="sm:col-span-2">
										<label
											for="learner-email"
											class="mb-1 block text-sm font-medium text-ink-gray-8"
											>{{ __('Learner email') }}</label
										><input
											id="learner-email"
											v-model="learnerEmail"
											type="email"
											required
											autocomplete="email"
											class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9"
										/>
									</div>
									<div>
										<label
											for="learner-first"
											class="mb-1 block text-sm font-medium text-ink-gray-8"
											>{{ __('First name for new user') }}</label
										><input
											id="learner-first"
											v-model="learnerFirst"
											type="text"
											maxlength="140"
											autocomplete="given-name"
											class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9"
										/>
									</div>
									<div>
										<label
											for="learner-last"
											class="mb-1 block text-sm font-medium text-ink-gray-8"
											>{{ __('Last name') }}</label
										><input
											id="learner-last"
											v-model="learnerLast"
											type="text"
											maxlength="140"
											autocomplete="family-name"
											class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9"
										/>
									</div>
									<p
										v-if="assignError"
										role="alert"
										class="text-sm text-red-600 sm:col-span-2"
									>
										{{ assignError }}
									</p>
									<button
										type="submit"
										:disabled="
											!course ||
											!learnerEmail ||
											assigning ||
											workspace.data.organization.status !== 'Active'
										"
										class="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
									>
										{{ assigning ? __('Assigning…') : __('Invite & assign') }}
									</button>
								</form>
							</div>
							<div class="mt-6 border-t border-outline-gray-2 pt-5">
								<h3 class="font-semibold text-ink-gray-9">
									{{ __('Import a roster') }}
								</h3>
								<p class="mt-1 text-sm text-ink-gray-6">
									{{
										__(
											'CSV columns: email,first_name,last_name. Up to 500 learners. Preview before committing.',
										)
									}}
								</p>
								<input
									type="file"
									accept=".csv,text/csv"
									class="mt-3 block w-full rounded-lg border border-outline-gray-2 bg-surface-base p-3 text-sm text-ink-gray-8"
									@change="readRoster"
								/>
								<label
									class="mt-3 flex items-center gap-2 text-sm text-ink-gray-7"
									><input
										v-model="createMissing"
										type="checkbox"
										@change="preview = null"
									/>{{
										__('Create accounts for learners not yet on the platform')
									}}</label
								>
								<p v-if="createMissing" class="mt-1 text-xs text-ink-gray-5">
									{{
										__('Welcome emails require outgoing mail to be configured.')
									}}
								</p>
								<div
									v-if="preview"
									class="mt-4 rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-4 text-sm text-ink-gray-8"
								>
									<p>
										{{ preview.rows }} {{ __('rows') }} ·
										{{ preview.new_users }} {{ __('new users') }} ·
										{{ preview.to_assign }} {{ __('new assignments') }} ·
										{{ preview.already_assigned }} {{ __('already assigned') }}
									</p>
									<ul
										v-if="preview.errors?.length"
										class="mt-2 list-disc ps-5 text-red-600"
									>
										<li v-for="error in preview.errors" :key="error.row">
											{{ __('Row') }} {{ error.row }}: {{ error.message }}
										</li>
									</ul>
									<p v-if="preview.applied" class="mt-2 text-green-700">
										{{ __('Roster imported and assigned.') }}
									</p>
								</div>
								<p
									v-if="rosterError"
									role="alert"
									class="mt-3 text-sm text-red-600"
								>
									{{ rosterError }}
								</p>
								<div class="mt-4 flex flex-wrap gap-2">
									<button
										type="button"
										:disabled="
											!course ||
											!csvText ||
											rosterBusy ||
											workspace.data.organization.status !== 'Active'
										"
										class="rounded-lg border border-outline-gray-2 px-4 py-2.5 text-sm font-medium text-ink-gray-9 disabled:opacity-50"
										@click="submitRoster(true)"
									>
										{{ __('Preview roster') }}</button
									><button
										type="button"
										:disabled="
											!preview?.ok ||
											preview?.applied ||
											rosterBusy ||
											workspace.data.organization.status !== 'Active'
										"
										class="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50"
										@click="submitRoster(false)"
									>
										{{ __('Import & assign') }}
									</button>
								</div>
							</div>
						</template>
					</section>
				</div>

				<section
					class="mt-7 overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-elevation-1"
				>
					<div
						class="flex flex-wrap items-center justify-between gap-3 border-b border-outline-gray-2 p-6"
					>
						<div>
							<div
								class="flex size-9 items-center justify-center rounded-lg bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
							>
								3
							</div>
							<h2 class="mt-4 text-xl font-semibold text-ink-gray-9">
								{{ __('Training roster') }}
							</h2>
							<p class="mt-1 text-sm text-ink-gray-6">
								{{
									__(
										'Learners attached to this client through course assignments.',
									)
								}}
							</p>
						</div>
						<router-link
							:to="{
								name: 'Statistics',
								query: { organization: props.organization },
							}"
							class="text-sm font-medium text-ink-blue-6 hover:underline"
							>{{ __('Full analytics') }} →</router-link
						>
					</div>
					<div
						v-if="!workspace.data.assignments.length"
						class="p-8 text-sm text-ink-gray-6"
					>
						{{
							__(
								'No assignments yet. Choose a course above and add a learner or import a roster.',
							)
						}}
					</div>
					<div v-else class="overflow-x-auto">
						<table class="w-full text-left text-sm">
							<thead class="bg-surface-gray-1 text-ink-gray-6">
								<tr>
									<th class="px-6 py-3 font-medium">{{ __('Learner') }}</th>
									<th class="px-6 py-3 font-medium">{{ __('Course') }}</th>
									<th class="px-6 py-3 font-medium">{{ __('Progress') }}</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-outline-gray-2">
								<tr v-for="row in workspace.data.assignments" :key="row.name">
									<td class="px-6 py-3">
										<p class="font-medium text-ink-gray-9">
											{{ row.full_name || row.member }}
										</p>
										<p class="text-xs text-ink-gray-5">{{ row.member }}</p>
									</td>
									<td class="px-6 py-3 text-ink-gray-8">
										{{ row.course_title || row.course }}
									</td>
									<td class="px-6 py-3 text-ink-gray-8">
										{{ Math.round(row.progress || 0) }}%
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</section>
			</template>
		</template>
	</div>
</template>

<script setup>
import { call, createResource, toast, usePageMeta } from 'frappe-ui'
import { computed, inject, ref, watch } from 'vue'
import { sessionStore } from '@/stores/session'
import { notifyMembersChanged } from '@/stores/members'

const props = defineProps({ organization: { type: String, required: true } })
const user = inject('$user')
const { brand } = sessionStore()
const isAdmin = computed(
	() => !!(user.data?.is_moderator || user.data?.is_system_manager),
)
const workspace = createResource({
	url: 'lms.lms.admin_learning.get_organization_workspace',
	makeParams: () => ({ name: props.organization }),
	auto: false,
})
const contactEmail = ref('')
const notes = ref('')
const savingProfile = ref(false)
const profileError = ref('')
const course = ref('')
const learnerEmail = ref('')
const learnerFirst = ref('')
const learnerLast = ref('')
const assigning = ref(false)
const assignError = ref('')
const csvText = ref('')
const createMissing = ref(true)
const preview = ref(null)
const rosterBusy = ref(false)
const rosterError = ref('')

watch(
	() => [isAdmin.value, props.organization],
	([allowed]) => {
		if (allowed) workspace.fetch()
	},
	{ immediate: true },
)

watch(
	() => workspace.data?.organization,
	(organization) => {
		if (!organization) return
		contactEmail.value = organization.contact_email || ''
		notes.value = organization.notes || ''
	},
)

async function saveProfile() {
	if (savingProfile.value) return
	savingProfile.value = true
	profileError.value = ''
	try {
		await call('lms.lms.admin_learning.update_organization', {
			name: props.organization,
			contact_email: contactEmail.value.trim(),
			notes: notes.value.trim(),
		})
		await workspace.reload()
		toast.success(__('Client profile saved'))
	} catch {
		profileError.value = __(
			'Unable to save this profile. Check the contact email and try again.',
		)
	} finally {
		savingProfile.value = false
	}
}

async function assignOne() {
	if (!course.value || !learnerEmail.value || assigning.value) return
	assigning.value = true
	assignError.value = ''
	try {
		const result = await call('lms.lms.admin_learning.assign_client_learner', {
			organization: props.organization,
			course: course.value,
			email: learnerEmail.value.trim(),
			first_name: learnerFirst.value.trim(),
			last_name: learnerLast.value.trim(),
		})
		if (!result.assigned) {
			assignError.value = __(
				'This learner is already assigned to the selected course for this client.',
			)
			return
		}
		learnerEmail.value = ''
		learnerFirst.value = ''
		learnerLast.value = ''
		await workspace.reload()
		if (result.created_user) notifyMembersChanged()
		toast.success(
			result.created_user
				? result.welcome_email_queued
					? __('Learner assigned; welcome email queued')
					: __('Learner assigned; check outgoing email before sharing access')
				: __('Learner assigned'),
		)
	} catch (error) {
		assignError.value =
			error?.messages?.[0] ||
			__('Unable to assign this learner. Check their details and course.')
	} finally {
		assigning.value = false
	}
}

async function readRoster(event) {
	preview.value = null
	rosterError.value = ''
	csvText.value = ''
	const file = event.target.files?.[0]
	if (!file) return
	if (file.size > 100_000) {
		rosterError.value = __('CSV must be smaller than 100 KB.')
		return
	}
	csvText.value = await file.text()
}

async function submitRoster(dryRun) {
	if (!course.value || !csvText.value || rosterBusy.value) return
	rosterBusy.value = true
	rosterError.value = ''
	try {
		preview.value = await call('lms.lms.admin_learning.bulk_assign_course', {
			course: course.value,
			csv_text: csvText.value,
			create_missing: createMissing.value ? 1 : 0,
			organization: props.organization,
			dry_run: dryRun ? 1 : 0,
		})
		if (preview.value.applied) {
			await workspace.reload()
			notifyMembersChanged()
			toast.success(__('Roster imported and assigned'))
		}
	} catch (error) {
		rosterError.value =
			error?.messages?.[0] || __('Unable to process this roster.')
	} finally {
		rosterBusy.value = false
	}
}

usePageMeta(() => ({
	title:
		workspace.data?.organization?.organization_name || __('Client workspace'),
	icon: brand.favicon,
}))
</script>
