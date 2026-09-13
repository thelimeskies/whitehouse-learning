<template>
	<div class="">
		<PageHeader :breadcrumbs="breadcrumbs" />
		<div v-if="!isAdmin" class="p-5 text-ink-gray-6">
			{{ __('Analytics are available to administrators only.') }}
		</div>
		<div
			v-else-if="chartDetails.loading && !chartDetails.data"
			class="flex flex-1 items-center justify-center p-5"
		>
			<LoadingIndicator class="size-5 text-ink-gray-5" />
		</div>
		<div v-else-if="chartDetails.data" class="p-5">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
				<Tooltip :text="__('Published Courses')">
					<NumberChart
						class="border rounded-md"
						:config="{ title: 'Courses', value: chartDetails.data.courses }"
					/>
				</Tooltip>
				<Tooltip :text="__('Active Members')">
					<NumberChart
						class="border rounded-md"
						:config="{ title: 'Signups', value: chartDetails.data.users }"
					/>
				</Tooltip>
				<Tooltip :text="__('Course Enrollments')">
					<NumberChart
						class="border rounded-md"
						:config="{
							title: 'Enrollments',
							value: chartDetails.data.enrollments,
						}"
					/>
				</Tooltip>
				<Tooltip :text="__('Course Completions')">
					<NumberChart
						class="border rounded-md"
						:config="{
							title: 'Completions',
							value: chartDetails.data.completions,
						}"
					/>
				</Tooltip>
				<Tooltip :text="__('Certified Members')">
					<NumberChart
						class="border rounded-md"
						:config="{
							title: 'Certifications',
							value: chartDetails.data.certifications,
						}"
					/>
				</Tooltip>
			</div>
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
				<div class="border rounded-md min-h-72">
					<AxisChart
						v-if="signupsChart.data"
						:config="{
							data: signupsChart.data,
							title: 'Signups',
							subtitle: 'Signups per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Signups',
							},
							series: [{ name: 'signups', type: 'line', showDataPoints: true }],
						}"
					/>
				</div>
				<div class="border rounded-md min-h-72">
					<AxisChart
						v-if="enrollmentChart.data"
						:config="{
							data: enrollmentChart.data,
							title: 'Enrollments',
							subtitle: 'Enrollments per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Enrollments',
							},
							series: [
								{ name: 'enrollments', type: 'line', showDataPoints: true },
							],
						}"
					/>
				</div>
				<div class="border rounded-md">
					<AxisChart
						v-if="certification.data"
						:config="{
							data: certification.data,
							title: 'Certifications',
							subtitle: 'Certifications per day',
							xAxis: {
								key: 'date',
								type: 'time',
								title: 'Date',
								timeGrain: 'day',
							},
							yAxis: {
								title: 'Certifications',
							},
							series: [
								{
									name: 'certifications',
									type: 'line',
									showDataPoints: true,
								},
							],
						}"
					/>
				</div>
				<div v-if="hasCompletions" class="border rounded-md">
					<DonutChart
						v-if="courseCompletion.data"
						:config="{
							data: courseCompletion.data,
							title: 'Completions',
							subtitle: 'Course Completion',
							categoryColumn: 'label',
							valueColumn: 'value',
						}"
					/>
				</div>
			</div>
			<section class="mt-8 space-y-5">
				<div class="rounded border p-4">
					<h2 class="text-lg-semibold">{{ __('Client organizations') }}</h2>
					<p class="mt-1 text-p-sm text-ink-gray-6">{{ __('Whitehouse manages training clients centrally. Learners do not sign up or enroll through an organization.') }}</p>
					<div class="mt-3 flex flex-wrap gap-2">
						<input v-model="newOrganization" type="text" maxlength="140" :placeholder="__('Organization name')" class="min-w-56 flex-1 rounded border border-outline-gray-2 p-2 text-p-sm" />
						<button class="rounded bg-ink-gray-9 px-4 py-2 text-p-sm text-white" :disabled="!newOrganization.trim() || creatingOrganization" @click="addOrganization">{{ __('Add organization') }}</button>
					</div>
					<p v-if="organizationError" class="mt-2 text-p-sm text-red-700">{{ organizationError }}</p>
				</div>
				<div class="flex flex-wrap items-end justify-between gap-3">
					<div>
						<h2 class="text-2xl-semibold text-ink-gray-9">{{ __('Learning outcomes') }}</h2>
						<p class="text-p-sm text-ink-gray-6">{{ __('Assignments, engagement, completion, and learners needing attention.') }}</p>
					</div>
					<div class="flex flex-wrap gap-2">
					<select v-model="selectedOrganization" class="rounded border border-outline-gray-2 bg-white p-2 text-p-sm" @change="analytics.fetch()">
						<option value="">{{ __('All organizations and direct training') }}</option>
						<option v-for="item in organizations" :key="item.name" :value="item.name">{{ item.organization_name }}</option>
					</select>
					<select v-model="selectedCourse" class="rounded border border-outline-gray-2 bg-white p-2 text-p-sm" @change="analytics.fetch()">
						<option value="">{{ __('All courses') }}</option>
						<option v-for="course in courseOptions" :key="course.name" :value="course.name">{{ course.title }}</option>
					</select>
					</div>
				</div>
				<div v-if="analytics.data" class="space-y-5">
					<div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
						<NumberChart class="rounded border" :config="{ title: 'Assignments', value: analytics.data.summary.assignments || 0 }" />
						<NumberChart class="rounded border" :config="{ title: 'Not started', value: analytics.data.summary.not_started || 0 }" />
						<NumberChart class="rounded border" :config="{ title: 'In progress', value: analytics.data.summary.in_progress || 0 }" />
						<NumberChart class="rounded border" :config="{ title: 'Completed', value: analytics.data.summary.completed || 0 }" />
						<NumberChart class="rounded border" :config="{ title: 'Unique learners', value: analytics.data.summary.learners || 0 }" />
						<NumberChart class="rounded border" :config="{ title: 'Average progress', value: `${analytics.data.summary.average_progress || 0}%` }" />
						<NumberChart class="rounded border" :config="{ title: 'Completion rate', value: `${completionRate}%` }" />
						<NumberChart class="rounded border" :config="{ title: 'Inactive 14 days', value: analytics.data.summary.inactive_14_days || 0 }" />
					</div>
					<div v-if="analytics.data.trend?.length" class="min-h-72 rounded border">
						<AxisChart :config="{
							data: analytics.data.trend.map((row) => ({ date: new Date(row.date), assignments: row.assignments })),
							title: 'Assignment trend',
							subtitle: 'New course assignments in the last 30 days',
							xAxis: { key: 'date', type: 'time', title: 'Date', timeGrain: 'day' },
							yAxis: { title: 'Assignments' },
							series: [{ name: 'assignments', type: 'line', showDataPoints: true }],
						}" />
					</div>
					<div class="overflow-x-auto rounded border">
						<h3 class="p-4 text-lg-semibold">{{ __('Course performance') }}</h3>
						<table class="w-full text-left text-p-sm">
							<thead class="bg-surface-gray-1"><tr><th class="p-3">{{ __('Course') }}</th><th class="p-3">{{ __('Assigned') }}</th><th class="p-3">{{ __('Not started') }}</th><th class="p-3">{{ __('In progress') }}</th><th class="p-3">{{ __('Completed') }}</th><th class="p-3">{{ __('Average progress') }}</th></tr></thead>
							<tbody><tr v-for="course in analytics.data.courses" :key="course.name" class="border-t"><td class="p-3">{{ course.title }}</td><td class="p-3">{{ course.assignments }}</td><td class="p-3">{{ course.not_started }}</td><td class="p-3">{{ course.in_progress }}</td><td class="p-3">{{ course.completed }}</td><td class="p-3">{{ course.average_progress || 0 }}%</td></tr></tbody>
						</table>
					</div>
					<div class="overflow-x-auto rounded border">
						<h3 class="p-4 text-lg-semibold">{{ __('Organization performance') }}</h3>
						<p v-if="!analytics.data.organizations?.length" class="px-4 pb-4 text-p-sm text-ink-gray-6">{{ __('No client-assigned courses yet.') }}</p>
						<table v-else class="w-full text-left text-p-sm"><thead class="bg-surface-gray-1"><tr><th class="p-3">{{ __('Organization') }}</th><th class="p-3">{{ __('Learners') }}</th><th class="p-3">{{ __('Assignments') }}</th><th class="p-3">{{ __('Completed') }}</th><th class="p-3">{{ __('Average progress') }}</th></tr></thead><tbody><tr v-for="row in analytics.data.organizations" :key="row.organization" class="border-t"><td class="p-3">{{ row.organization }}</td><td class="p-3">{{ row.learners }}</td><td class="p-3">{{ row.assignments }}</td><td class="p-3">{{ row.completed }}</td><td class="p-3">{{ row.average_progress || 0 }}%</td></tr></tbody></table>
				</div>
				<div class="overflow-x-auto rounded border">
					<div class="flex flex-wrap items-center justify-between gap-2 p-4"><h3 class="text-lg-semibold">{{ __('Per-person learning progress') }}</h3><input v-model="learnerSearch" type="search" :placeholder="__('Search learner or email')" class="rounded border border-outline-gray-2 p-2 text-p-sm" /></div>
					<p class="px-4 pb-2 text-p-xs text-ink-gray-6">{{ __('Showing up to 1,000 course assignments. Video time is recorded by the learner player, not independently verified viewing. Last update is the enrollment record update.') }}</p>
					<p v-if="!filteredPeople.length" class="px-4 pb-4 text-p-sm text-ink-gray-6">{{ __('No matching learners.') }}</p>
					<table v-else class="w-full text-left text-p-sm"><thead class="bg-surface-gray-1"><tr><th class="p-3">{{ __('Learner') }}</th><th class="p-3">{{ __('Organization') }}</th><th class="p-3">{{ __('Course') }}</th><th class="p-3">{{ __('Progress') }}</th><th class="p-3">{{ __('Lessons complete') }}</th><th class="p-3">{{ __('Video minutes') }}</th><th class="p-3">{{ __('Best quiz') }}</th><th class="p-3">{{ __('Current lesson') }}</th><th class="p-3">{{ __('Last update') }}</th></tr></thead><tbody><tr v-for="row in filteredPeople" :key="`${row.member}-${row.course}`" class="border-t"><td class="p-3">{{ row.full_name || row.member }}<br /><span class="text-ink-gray-5">{{ row.member }}</span></td><td class="p-3">{{ row.organization || __('Direct') }}</td><td class="p-3">{{ row.course_title }}</td><td class="p-3">{{ row.progress }}%</td><td class="p-3">{{ row.lessons_completed || 0 }}</td><td class="p-3">{{ row.recorded_video_minutes || 0 }}</td><td class="p-3">{{ row.best_quiz_percent == null ? '—' : `${row.best_quiz_percent}%` }}</td><td class="p-3">{{ row.current_lesson || '—' }}</td><td class="p-3">{{ row.last_enrollment_update }}</td></tr></tbody></table>
				</div>
				<div class="overflow-x-auto rounded border">
						<h3 class="p-4 text-lg-semibold">{{ __('Needs attention') }}</h3>
						<p class="px-4 pb-3 text-p-sm text-ink-gray-6">{{ __('Incomplete assignments whose enrollment record has not updated for at least 14 days.') }}</p>
						<p v-if="!analytics.data.at_risk?.length" class="px-4 pb-4 text-p-sm text-ink-gray-6">{{ __('No learners currently match this rule.') }}</p>
						<table v-else class="w-full text-left text-p-sm"><thead class="bg-surface-gray-1"><tr><th class="p-3">{{ __('Learner') }}</th><th class="p-3">{{ __('Course') }}</th><th class="p-3">{{ __('Progress') }}</th><th class="p-3">{{ __('Last activity') }}</th></tr></thead><tbody><tr v-for="row in analytics.data.at_risk" :key="`${row.member}-${row.course}`" class="border-t"><td class="p-3">{{ row.full_name || row.member }}<br /><span class="text-ink-gray-5">{{ row.member }}</span></td><td class="p-3">{{ row.course_title }}</td><td class="p-3">{{ row.progress || 0 }}%</td><td class="p-3">{{ row.last_activity }}</td></tr></tbody></table>
					</div>
				</div>
			</section>
		</div>
	</div>
</template>
<script setup>
import {
	AxisChart,
	call,
	createResource,
	DonutChart,
	LoadingIndicator,
	NumberChart,
	Tooltip,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, ref, watch } from 'vue'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import { sessionStore } from '../stores/session'

const { brand } = sessionStore()
const user = inject('$user')
const isAdmin = computed(() => !!(user.data?.is_moderator || user.data?.is_system_manager))
const selectedCourse = ref('')
const selectedOrganization = ref('')
const courseOptions = ref([])
const organizations = ref([])
const newOrganization = ref('')
const organizationError = ref('')
const creatingOrganization = ref(false)
const learnerSearch = ref('')
const filteredPeople = computed(() => {
	const query = learnerSearch.value.trim().toLowerCase()
	const people = analytics.data?.people || []
	return query ? people.filter((row) => `${row.full_name} ${row.member}`.toLowerCase().includes(query)) : people
})

async function addOrganization() {
	if (!newOrganization.value.trim() || creatingOrganization.value) return
	creatingOrganization.value = true
	organizationError.value = ''
	try {
		await call('lms.lms.admin_learning.create_organization', { organization_name: newOrganization.value.trim() })
		organizations.value = await call('lms.lms.admin_learning.get_organizations')
		newOrganization.value = ''
	} catch (error) {
		organizationError.value = __('Unable to add organization. Check the name and try again.')
	} finally {
		creatingOrganization.value = false
	}
}

const breadcrumbs = computed(() => {
	return [
		{
			label: __('Statistics'),
			route: {
				name: 'Statistics',
			},
		},
	]
})

const chartDetails = createResource({
	url: 'lms.lms.api.get_chart_details',
	cache: ['statistics'],
	auto: false,
})

const signupsChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	params: {
		chart_name: 'New Signups',
	},
	auto: false,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				signups: item.count,
			}
		})
	},
})

const enrollmentChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	cache: ['enrollments'],
	params: {
		chart_name: 'Course Enrollments',
	},
	auto: false,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				enrollments: item.count,
			}
		})
	},
})

const certification = createResource({
	url: 'lms.lms.utils.get_chart_data',
	cache: ['certifications'],
	params: {
		chart_name: 'Certification',
	},
	auto: false,
	transform(data) {
		return data.map((item) => {
			return {
				date: new Date(item.date),
				certifications: item.count,
			}
		})
	},
})

const courseCompletion = createResource({
	url: 'lms.lms.utils.get_course_completion_data',
	auto: false,
	cache: ['courseCompletion'],
})

// A donut with zero completions conveys nothing, so hide it until at least one
// learner has completed a course.
const hasCompletions = computed(() => {
	const completed = courseCompletion.data?.find((d) => d.label === 'Completed')
	return (completed?.value || 0) > 0
})

const analytics = createResource({
	url: 'lms.lms.admin_learning.get_admin_learning_analytics',
	makeParams: () => ({ course: selectedCourse.value || null, organization: selectedOrganization.value || null }),
	auto: false,
})

const completionRate = computed(() => {
	const summary = analytics.data?.summary
	return summary?.assignments
		? Math.round(((summary.completed || 0) / summary.assignments) * 100)
		: 0
})

watch(() => analytics.data?.courses, (courses) => {
	if (!selectedCourse.value && courses) courseOptions.value = courses
})

watch(isAdmin, (allowed) => {
	if (!allowed) return
	chartDetails.fetch()
	signupsChart.fetch()
	enrollmentChart.fetch()
	certification.fetch()
	courseCompletion.fetch()
	analytics.fetch()
	call('lms.lms.admin_learning.get_organizations').then((items) => { organizations.value = items })
}, { immediate: true })

usePageMeta(() => {
	return {
		title: __('Statistics'),
		icon: brand.favicon,
	}
})
</script>
