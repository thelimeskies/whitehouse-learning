<template>
	<div v-if="batch.data" class="border-2 rounded-md lg:w-72">
		<VideoPreview
			:video-link="batch.data.video_link"
			:fallback-image="batch.data.image"
		/>
		<div class="p-5">
			<Badge
				v-if="batch.data.seat_count && batch.data.seats_left > 0"
				variant="subtle"
				theme="green"
				size="md"
				:class="
					batch.data.amount || batch.data.courses.length
						? 'float-end'
						: 'w-fit mb-4'
				"
				:label="
					batch.data.seats_left +
					' ' +
					(batch.data.seats_left > 1 ? __('Seats Left') : __('Seat Left'))
				"
			/>
			<Badge
				v-else-if="batch.data.seat_count && batch.data.seats_left <= 0"
				variant="subtle"
				theme="red"
				size="md"
				class="float-end"
				:label="__('Sold Out')"
			/>
			<div
				v-if="batch.data.amount"
				class="text-lg-semibold mb-5 text-ink-gray-9"
			>
				{{ formatNumberIntoCurrency(batch.data.amount, batch.data.currency) }}
			</div>
			<div
				v-if="batch.data.courses.length"
				class="flex items-center mb-3 text-ink-gray-7"
			>
				<span class="lucide-book-open h-4 w-4 me-2" />
				<span> {{ batch.data.courses.length }} {{ __('Courses') }} </span>
			</div>
			<DateRange
				:startDate="batch.data.start_date"
				:endDate="batch.data.end_date"
				class="mb-3"
			/>
			<div class="flex items-center mb-3 text-ink-gray-7">
				<span class="lucide-clock h-4 w-4 me-2" />
				<span dir="ltr">
					{{ formatTime(batch.data.start_time) }} -
					{{ formatTime(batch.data.end_time) }}
				</span>
			</div>
			<div v-if="batch.data.timezone" class="flex items-center text-ink-gray-7">
				<span class="lucide-globe h-4 w-4 me-2" />
				<span>
					{{
						formatTimezone(
							batch.data.timezone,
							nextOccurrence(batch.data.start_date, batch.data.end_date)
						)
					}}
				</span>
			</div>

			<div v-if="!readOnlyMode && !canAccessBatch">
				<Badge theme="blue" size="lg" class="mt-4">
					{{ __('Your administrator assigns batches to learners') }}
				</Badge>
			</div>
		</div>
	</div>
</template>
<script setup>
import { inject, computed } from 'vue'
import { Badge } from 'frappe-ui'
import { formatNumberIntoCurrency, formatTime } from '@/utils'
import { formatTimezone, nextOccurrence } from '@/utils/timezone'
import DateRange from '@/components/Common/DateRange.vue'
import VideoPreview from '@/components/VideoPreview.vue'

const user = inject('$user')
const readOnlyMode = window.read_only_mode

const props = defineProps({
	batch: {
		type: Object,
		default: null,
	},
})

const isStudent = computed(() => {
	return user.data
		? props.batch.data?.students?.includes(user.data?.name)
		: false
})

const isModerator = computed(() => {
	return user.data?.is_moderator
})

const isEvaluator = computed(() => {
	return user.data?.is_evaluator
})

const canAccessBatch = computed(() => {
	if (!user.data) {
		return false
	}
	return isModerator.value || isStudent.value || isEvaluator.value
})

const isAdmin = computed(() => {
	return isModerator.value || isEvaluator.value
})
</script>
