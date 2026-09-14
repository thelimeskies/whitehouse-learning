<template>
	<div>
		<div class="mt-10 space-y-10">
			<UpcomingEvaluations :forHome="true" />
			<div v-if="myLiveClasses.data?.length">
				<h2 class="font-semibold text-md mb-3 text-ink-gray-9">
					{{ __('Upcoming Live Classes') }}
				</h2>
				<div class="grid grid-cols-1 md:grid-cols-4 gap-5">
					<div
						v-for="cls in myLiveClasses.data"
						:key="cls.name"
						class="border rounded-md hover:border-outline-gray-3 p-3"
					>
						<div class="font-semibold text-ink-gray-9 leading-5 mb-1">
							{{ cls.title }}
						</div>
						<div class="text-ink-gray-5 leading-5 mb-4">
							{{ cls.description }}
						</div>
						<div class="mt-auto space-y-4 text-ink-gray-7">
							<div class="flex items-center gap-x-2">
								<span class="lucide-calendar size-4" />
								<span>
									{{ dayjs(cls.date).format('DD MMMM YYYY') }}
								</span>
							</div>
							<div class="flex items-center gap-x-2">
								<span class="lucide-clock size-4" />
								<span>
									{{ formatTime(cls.time) }} -
									{{ dayjs(getClassEnd(cls)).format('HH:mm A') }}
								</span>
							</div>
							<div
								v-if="canAccessClass(cls)"
								class="flex items-center gap-x-2 text-ink-gray-9 mt-auto"
							>
								<a
									v-if="user.data?.is_moderator || user.data?.is_evaluator"
									:href="safeUrl(cls.start_url)"
									v-external
									class="cursor-pointer inline-flex items-center justify-center gap-2 transition-colors focus:outline-none text-ink-gray-8 bg-surface-gray-2 hover:bg-surface-gray-3 active:bg-surface-gray-4 focus-visible:ring focus-visible:ring-outline-gray-3 h-7 text-base px-2 rounded"
									:class="cls.join_url ? 'w-full' : 'w-1/2'"
								>
									<span class="lucide-monitor size-4" />
									{{ __('Start') }}
								</a>
								<a
									:href="safeUrl(cls.join_url)"
									v-external
									class="w-full cursor-pointer inline-flex items-center justify-center gap-2 transition-colors focus:outline-none text-ink-gray-8 bg-surface-gray-2 hover:bg-surface-gray-3 active:bg-surface-gray-4 focus-visible:ring focus-visible:ring-outline-gray-3 h-7 text-base px-2 rounded"
								>
									<span class="lucide-video size-4" />
									{{ __('Join') }}
								</a>
							</div>
							<Tooltip
								v-else-if="hasClassEnded(cls)"
								:text="__('This class has ended')"
								placement="right"
							>
								<div class="flex items-center gap-x-2 text-ink-amber-3 w-fit">
									<span class="lucide-info size-4" />
									<span>
										{{ __('Ended') }}
									</span>
								</div>
							</Tooltip>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div
			v-if="!myCourses.data && !myCourses.error"
			class="mt-10 rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-8 text-sm text-ink-gray-6"
		>
			{{ __('Loading your training…') }}
		</div>
		<div
			v-else-if="myCourses.error && !myCourses.data"
			class="mt-10 rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-8"
		>
			<h2 class="text-lg-semibold text-ink-gray-9">
				{{ __('Your training could not be loaded') }}
			</h2>
			<p class="mt-2 text-sm text-ink-gray-6">
				{{ __('Please try again in a moment.') }}
			</p>
			<button
				type="button"
				class="mt-5 rounded-lg bg-surface-blue-2 px-4 py-2 text-sm font-medium text-ink-blue-6"
				@click="myCourses.reload()"
			>
				{{ __('Try again') }}
			</button>
		</div>
		<section
			v-else-if="!visibleCourses.length"
			class="relative mt-10 overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-elevation-1 p-6 shadow-sm sm:p-10"
		>
			<div
				class="pointer-events-none absolute -right-16 -top-24 size-72 rounded-full bg-surface-blue-1 blur-3xl"
				aria-hidden="true"
			/>
			<div
				class="relative grid gap-9 lg:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)] lg:items-center"
			>
				<div>
					<div
						class="mb-6 flex size-14 items-center justify-center rounded-2xl bg-surface-blue-2 text-ink-blue-6"
					>
						<span class="lucide-book-open-check size-7" aria-hidden="true" />
					</div>
					<p
						class="text-xs font-semibold uppercase tracking-widest text-ink-blue-6"
					>
						{{ __('Your learning space') }}
					</p>
					<h2
						class="mt-3 max-w-xl text-3xl font-semibold leading-tight text-ink-gray-9 sm:text-4xl"
					>
						{{ __('Your next course is on its way') }}
					</h2>
					<p class="mt-4 max-w-xl text-base leading-7 text-ink-gray-6">
						{{
							__(
								'Whitehouse will add your training here when it is assigned. You do not need to enroll yourself.',
							)
						}}
					</p>
				</div>
				<div
					class="rounded-2xl border border-outline-gray-2 bg-surface-base p-6 shadow-sm"
				>
					<p
						class="text-xs font-semibold uppercase tracking-widest text-ink-gray-5"
					>
						{{ __('What happens next') }}
					</p>
					<div class="mt-6 space-y-6">
						<div class="flex gap-4">
							<span
								class="flex size-9 shrink-0 items-center justify-center rounded-full bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
								>01</span
							>
							<div>
								<p class="font-medium text-ink-gray-9">
									{{ __('Training is assigned') }}
								</p>
								<p class="mt-1 text-sm leading-5 text-ink-gray-6">
									{{ __('Your courses appear on this page.') }}
								</p>
							</div>
						</div>
						<div class="flex gap-4">
							<span
								class="flex size-9 shrink-0 items-center justify-center rounded-full bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
								>02</span
							>
							<div>
								<p class="font-medium text-ink-gray-9">
									{{ __('Learn at your pace') }}
								</p>
								<p class="mt-1 text-sm leading-5 text-ink-gray-6">
									{{ __('Open a course and pick up where you left off.') }}
								</p>
							</div>
						</div>
						<div class="flex gap-4">
							<span
								class="flex size-9 shrink-0 items-center justify-center rounded-full bg-surface-blue-2 text-sm font-semibold text-ink-blue-6"
								>03</span
							>
							<div>
								<p class="font-medium text-ink-gray-9">
									{{ __('See your progress') }}
								</p>
								<p class="mt-1 text-sm leading-5 text-ink-gray-6">
									{{ __('Your learning record updates as you go.') }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
		<div v-else class="mt-10">
			<div class="mb-5 flex flex-wrap items-end justify-between gap-4">
				<div>
					<p
						class="text-xs font-semibold uppercase tracking-widest text-ink-blue-6"
					>
						{{ __('Your learning') }}
					</p>
					<h2 class="mt-2 text-2xl font-semibold text-ink-gray-9">
						{{ __('Assigned courses') }}
					</h2>
					<p class="mt-1 text-sm text-ink-gray-6">
						{{ __('Continue your training and follow your progress.') }}
					</p>
				</div>
				<router-link
					:to="{
						name: 'Courses',
					}"
				>
					<span
						class="flex items-center gap-x-1 text-ink-blue-6 text-sm font-medium"
					>
						<span>
							{{ __('View all courses') }}
						</span>
						<span class="lucide-move-right size-3 rtl:rotate-180" />
					</span>
				</router-link>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
				<router-link
					v-for="course in visibleCourses"
					:key="course.name"
					:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
				>
					<CourseCard :course="course" />
				</router-link>
			</div>
		</div>

		<div v-if="myBatches.data?.length" class="mt-10">
			<div class="flex items-center justify-between mb-3">
				<h2 class="font-semibold text-md text-ink-gray-9">
					{{ __('My Batches') }}
				</h2>
				<router-link
					:to="{
						name: 'Batches',
					}"
				>
					<span class="flex items-center gap-x-1 text-ink-gray-5 text-xs">
						<span>
							{{ __('See all') }}
						</span>
						<span class="lucide-move-right size-3 rtl:rotate-180" />
					</span>
				</router-link>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
				<router-link
					v-for="batch in myBatches.data"
					:key="batch.name"
					:to="{ name: 'BatchDetail', params: { batchName: batch.name } }"
				>
					<BatchCard :batch="batch" />
				</router-link>
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed, inject } from 'vue'
import { createResource, Tooltip } from 'frappe-ui'
import { formatTime } from '@/utils'
import CourseCard from '@/components/CourseCard.vue'
import BatchCard from '@/pages/Batches/components/BatchCard.vue'
import UpcomingEvaluations from '@/components/UpcomingEvaluations.vue'
import { safeUrl } from '@/utils/safeUrl'

const dayjs = inject<any>('$dayjs')
const user = inject<any>('$user')

const props = defineProps<{
	myLiveClasses: any
}>()

const myCourses = createResource({
	url: 'lms.lms.api.get_my_courses',
	auto: true,
})

const visibleCourses = computed(() =>
	(myCourses.data || []).filter((course: any) => course?.name && course?.title),
)

const myBatches = createResource({
	url: 'lms.lms.api.get_my_batches',
	auto: true,
})

const getClassEnd = (cls: { date: string; time: string; duration: number }) => {
	const classStart = new Date(`${cls.date}T${cls.time}`)
	return new Date(classStart.getTime() + cls.duration * 60000)
}

const canAccessClass = (cls: {
	date: string
	time: string
	duration: number
}) => {
	if (cls.date < dayjs().format('YYYY-MM-DD')) return false
	if (cls.date > dayjs().format('YYYY-MM-DD')) return false
	if (hasClassEnded(cls)) return false
	return true
}

const hasClassEnded = (cls: {
	date: string
	time: string
	duration: number
}) => {
	const classEnd = getClassEnd(cls)
	const now = new Date()
	return now > classEnd
}
</script>
