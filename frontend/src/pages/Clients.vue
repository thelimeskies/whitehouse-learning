<template>
	<div class="mx-auto w-full max-w-7xl px-5 py-8 sm:px-8">
		<div
			v-if="!isAdmin"
			class="rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-8 text-ink-gray-6"
		>
			{{ __('Only Whitehouse administrators can manage clients and people.') }}
		</div>
		<template v-else>
			<header class="flex flex-wrap items-start justify-between gap-5">
				<div class="max-w-2xl">
					<p
						class="text-xs font-semibold uppercase tracking-widest text-ink-blue-6"
					>
						{{ __('Whitehouse operations') }}
					</p>
					<h1 class="mt-2 text-3xl font-semibold text-ink-gray-9">
						{{ __('Clients & people') }}
					</h1>
					<p class="mt-2 text-base leading-7 text-ink-gray-6">
						{{
							__(
								'Manage training clients and the people who learn with Whitehouse.',
							)
						}}
					</p>
				</div>
				<router-link
					:to="{ name: 'Statistics' }"
					class="inline-flex items-center gap-2 rounded-lg border border-outline-gray-2 bg-surface-elevation-1 px-4 py-2 text-sm font-medium text-ink-gray-8 hover:bg-surface-gray-2"
				>
					<span
						class="lucide-chart-no-axes-combined size-4"
						aria-hidden="true"
					/>
					{{ __('View learning outcomes') }}
				</router-link>
			</header>

			<div
				class="mt-8 inline-flex flex-wrap gap-1 rounded-xl border border-outline-gray-2 bg-surface-gray-1 p-1"
				role="tablist"
				:aria-label="__('Client management')"
			>
				<button
					type="button"
					role="tab"
					:aria-selected="currentTab === 'organizations'"
					class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
					:class="
						currentTab === 'organizations'
							? 'bg-surface-elevation-1 text-ink-gray-9 shadow-sm'
							: 'text-ink-gray-6 hover:text-ink-gray-9'
					"
					@click="currentTab = 'organizations'"
				>
					{{ __('Organizations') }}
				</button>
				<button
					type="button"
					role="tab"
					:aria-selected="currentTab === 'people'"
					class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
					:class="
						currentTab === 'people'
							? 'bg-surface-elevation-1 text-ink-gray-9 shadow-sm'
							: 'text-ink-gray-6 hover:text-ink-gray-9'
					"
					@click="currentTab = 'people'"
				>
					{{ __('Users & invites') }}
				</button>
			</div>

			<div
				v-if="currentTab === 'organizations'"
				class="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(300px,360px)]"
			>
				<section
					class="overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-elevation-1"
				>
					<div class="border-b border-outline-gray-2 p-6">
						<h2 class="text-xl font-semibold text-ink-gray-9">
							{{ __('Client organizations') }}
						</h2>
						<p class="mt-1 text-sm text-ink-gray-6">
							{{
								__(
									'Link course assignments to the client receiving the training.',
								)
							}}
						</p>
					</div>
					<div
						v-if="organizations.loading && !organizations.data"
						class="p-8 text-sm text-ink-gray-6"
					>
						{{ __('Loading organizations…') }}
					</div>
					<div
						v-else-if="organizations.error"
						class="p-8 text-sm text-ink-gray-6"
					>
						{{ __('Organizations could not be loaded.') }}
						<button
							type="button"
							class="ms-2 font-medium text-ink-blue-6"
							@click="organizations.reload()"
						>
							{{ __('Try again') }}
						</button>
					</div>
					<div
						v-else-if="!organizations.data?.length"
						class="p-8 text-sm text-ink-gray-6"
					>
						{{
							__(
								'No clients added yet. Create the first organization to begin.',
							)
						}}
					</div>
					<div v-else class="divide-y divide-outline-gray-2">
						<div
							v-for="item in organizations.data"
							:key="item.name"
							class="flex flex-wrap items-center justify-between gap-3 px-6 py-4"
						>
							<div class="flex min-w-0 items-center gap-3">
								<span
									class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-surface-blue-2 text-ink-blue-6"
									><span class="lucide-building-2 size-5" aria-hidden="true"
								/></span>
								<div class="min-w-0">
									<p class="truncate font-medium text-ink-gray-9">
										{{ item.organization_name }}
									</p>
									<p class="text-xs text-ink-gray-5">{{ item.status }}</p>
								</div>
							</div>
							<div class="flex items-center gap-4">
								<router-link
									:to="{
										name: 'Statistics',
										query: { organization: item.name },
									}"
									class="text-sm font-medium text-ink-blue-6 hover:underline"
									>{{ __('View outcomes') }}</router-link
								>
								<button
									type="button"
									:disabled="updatingOrganization === item.name"
									class="text-sm text-ink-gray-6 hover:text-ink-gray-9 disabled:opacity-50"
									@click="toggleOrganization(item)"
								>
									{{ item.status === 'Active' ? __('Pause') : __('Activate') }}
								</button>
							</div>
						</div>
					</div>
				</section>
				<section
					class="h-fit rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-6"
				>
					<div
						class="flex size-11 items-center justify-center rounded-xl bg-surface-blue-2 text-ink-blue-6"
					>
						<span class="lucide-plus size-5" aria-hidden="true" />
					</div>
					<h2 class="mt-5 text-lg font-semibold text-ink-gray-9">
						{{ __('Add an organization') }}
					</h2>
					<p class="mt-1 text-sm leading-6 text-ink-gray-6">
						{{
							__(
								'Add a training client before assigning its people to a course.',
							)
						}}
					</p>
					<form class="mt-5 space-y-3" @submit.prevent="addOrganization">
						<label
							for="client-organization-name"
							class="block text-sm font-medium text-ink-gray-8"
							>{{ __('Organization name') }}</label
						>
						<input
							id="client-organization-name"
							v-model="newOrganization"
							type="text"
							maxlength="140"
							autocomplete="organization"
							:placeholder="__('e.g. Acme Group')"
							class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<p
							v-if="organizationError"
							role="alert"
							class="text-sm text-red-600"
						>
							{{ organizationError }}
						</p>
						<button
							type="submit"
							:disabled="!newOrganization.trim() || creatingOrganization"
							class="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
						>
							{{
								creatingOrganization ? __('Adding…') : __('Add organization')
							}}
						</button>
					</form>
				</section>
			</div>

			<div v-else class="mt-6 space-y-5">
				<div
					class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-outline-gray-2 bg-surface-blue-1 p-5 sm:p-6"
				>
					<div class="max-w-2xl">
						<h2 class="text-lg font-semibold text-ink-gray-9">
							{{ __('Invite people, then assign their training') }}
						</h2>
						<p class="mt-1 text-sm leading-6 text-ink-gray-6">
							{{
								__(
									'Learners receive a welcome email when outgoing mail is configured. Choose a client organization when assigning a course, not when inviting a learner.',
								)
							}}
						</p>
					</div>
					<router-link
						:to="{ name: 'Courses' }"
						class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
						>{{ __('Go to courses')
						}}<span class="lucide-arrow-right size-4" aria-hidden="true"
					/></router-link>
				</div>
				<section
					class="rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-5 sm:p-6"
				>
					<h2 class="text-lg font-semibold text-ink-gray-9">
						{{ __('Invite a learner') }}
					</h2>
					<p class="mt-1 text-sm text-ink-gray-6">
						{{
							__(
								'Create a learner account with an email invitation. No course is assigned until you choose one.',
							)
						}}
					</p>
					<form
						class="mt-5 grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,1fr)_auto] md:items-end"
						@submit.prevent="inviteLearner"
					>
						<div>
							<label
								for="invite-email"
								class="mb-1.5 block text-sm font-medium text-ink-gray-8"
								>{{ __('Email') }}</label
							><input
								id="invite-email"
								v-model="inviteEmail"
								type="email"
								required
								autocomplete="email"
								:placeholder="__('person@example.com')"
								class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>
						<div>
							<label
								for="invite-first-name"
								class="mb-1.5 block text-sm font-medium text-ink-gray-8"
								>{{ __('First name') }}</label
							><input
								id="invite-first-name"
								v-model="inviteFirstName"
								type="text"
								required
								maxlength="140"
								autocomplete="given-name"
								class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>
						<div>
							<label
								for="invite-last-name"
								class="mb-1.5 block text-sm font-medium text-ink-gray-8"
								>{{ __('Last name') }}</label
							><input
								id="invite-last-name"
								v-model="inviteLastName"
								type="text"
								maxlength="140"
								autocomplete="family-name"
								class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>
						<button
							type="submit"
							:disabled="inviting"
							class="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
						>
							{{ inviting ? __('Sending…') : __('Invite learner') }}
						</button>
					</form>
					<p
						v-if="inviteMessage"
						role="status"
						class="mt-3 text-sm text-ink-gray-7"
					>
						{{ inviteMessage }}
					</p>
					<p v-if="inviteError" role="alert" class="mt-3 text-sm text-red-600">
						{{ inviteError }}
					</p>
				</section>
				<div
					class="min-h-[520px] overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-elevation-1"
				>
					<Members
						:label="__('Users')"
						:description="
							__(
								'Add or invite learners, search existing people, and manage access roles.',
							)
						"
					/>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup>
import { call, createResource, toast, usePageMeta } from 'frappe-ui'
import { computed, inject, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Members from '@/components/Settings/Members.vue'
import { sessionStore } from '@/stores/session'
import { notifyMembersChanged } from '@/stores/members'

const user = inject('$user')
const route = useRoute()
const router = useRouter()
const { brand } = sessionStore()
const isAdmin = computed(
	() => !!(user.data?.is_moderator || user.data?.is_system_manager),
)
const currentTab = ref(
	route.query.tab === 'people' ? 'people' : 'organizations',
)
const newOrganization = ref('')
const organizationError = ref('')
const creatingOrganization = ref(false)
const updatingOrganization = ref('')
const inviteEmail = ref('')
const inviteFirstName = ref('')
const inviteLastName = ref('')
const inviting = ref(false)
const inviteMessage = ref('')
const inviteError = ref('')
const organizations = createResource({
	url: 'lms.lms.admin_learning.get_organizations',
	auto: false,
})

watch(
	isAdmin,
	(allowed) => {
		if (allowed) organizations.fetch()
	},
	{ immediate: true },
)

watch(currentTab, (tab) => {
	router.replace({ name: 'Clients', query: tab === 'people' ? { tab } : {} })
})

async function addOrganization() {
	if (
		!isAdmin.value ||
		!newOrganization.value.trim() ||
		creatingOrganization.value
	)
		return
	creatingOrganization.value = true
	organizationError.value = ''
	try {
		await call('lms.lms.admin_learning.create_organization', {
			organization_name: newOrganization.value.trim(),
		})
		newOrganization.value = ''
		await organizations.reload()
		toast.success(__('Organization added'))
	} catch {
		organizationError.value = __(
			'Unable to add this organization. Check the name and try again.',
		)
	} finally {
		creatingOrganization.value = false
	}
}

async function toggleOrganization(item) {
	if (!isAdmin.value || updatingOrganization.value) return
	updatingOrganization.value = item.name
	try {
		await call('lms.lms.admin_learning.set_organization_status', {
			name: item.name,
			status: item.status === 'Active' ? 'Inactive' : 'Active',
		})
		await organizations.reload()
	} catch {
		toast.error(__('Unable to update this organization.'))
	} finally {
		updatingOrganization.value = ''
	}
}

async function inviteLearner() {
	if (!isAdmin.value || inviting.value) return
	inviting.value = true
	inviteError.value = ''
	inviteMessage.value = ''
	try {
		const result = await call('lms.lms.admin_learning.invite_learner', {
			email: inviteEmail.value.trim(),
			first_name: inviteFirstName.value.trim(),
			last_name: inviteLastName.value.trim(),
		})
		inviteEmail.value = ''
		inviteFirstName.value = ''
		inviteLastName.value = ''
		inviteMessage.value = result.welcome_email_queued
			? __(
					'Learner created and welcome email queued. Assign a course to give them training.',
				)
			: __(
					'Learner created, but no welcome email was queued. Check outgoing email before sharing access.',
				)
		notifyMembersChanged()
	} catch {
		inviteError.value = __(
			'Unable to invite this learner. Check the address or whether the user already exists.',
		)
	} finally {
		inviting.value = false
	}
}

usePageMeta(() => ({ title: __('Clients & people'), icon: brand.favicon }))
</script>
