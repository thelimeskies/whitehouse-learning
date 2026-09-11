<template>
	<img
		:src="safeUrl(whitehouseLearningMark)"
		alt="Whitehouse Learning"
		width="80"
		height="80"
		class="object-contain"
	/>
</template>

<script setup>
import whitehouseLearningMark from '@/client/assets/whitehouse-learning-mark.png'
import { safeUrl } from '@/utils/safeUrl'
</script>
