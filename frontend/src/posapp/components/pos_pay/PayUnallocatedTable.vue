<!-- eslint-disable vue/multi-word-component-names -->
<template>
	<div v-if="posProfile?.posa_allow_reconcile_payments">
		<v-row>
			<v-col md="7" cols="12">
				<p>
					<strong>{{ resolvedSectionTitle }}</strong>
					<span v-if="totalUnallocated" class="text-primary">
						{{ __("- Total Unallocated") }} :
						<span class="posa-price-line">
							<span class="currency-symbol">{{ currencySymbol(posProfile.currency) }}</span>
							<span class="amount-value">{{
								formatCurrency(totalUnallocated)
							}}</span>
						</span>
					</span>
				</p>
			</v-col>
			<v-col md="5" cols="12">
				<p v-if="totalSelected" class="golden--text text-end">
					<span>{{ __("Total Selected :") }}</span>
					<span class="posa-price-line">
						<span class="currency-symbol">{{ currencySymbol(posProfile.currency) }}</span>
						<span class="amount-value">{{ formatCurrency(totalSelected) }}</span>
					</span>
				</p>
			</v-col>
		</v-row>
		<v-data-table
			:headers="headers"
			:items="payments"
			item-key="name"
			class="elevation-1 mt-0"
			:loading="loading"
			:row-props="paymentRowProps"
		>
			<template v-slot:item.select="{ item }">
				<v-checkbox
					v-model="internalSelectedPayments"
					:value="item"
					color="primary"
					hide-details
					@click.stop
				></v-checkbox>
			</template>
			<template v-slot:item.mode_of_payment="{ item }">
				<span>
					{{ item?.is_credit_note ? __("Credit Note") : item?.mode_of_payment }}
				</span>
			</template>
			<template v-slot:item.reference_invoice="{ item }">
				<span v-if="item?.is_credit_note && item?.reference_invoice">
					{{ item.reference_invoice }}
				</span>
			</template>
			<template v-slot:item.paid_amount="{ item }">
				<span class="posa-price-line">
					<span class="currency-symbol">{{ currencySymbol(item.currency) }}</span>
					<span class="amount-value">{{ formatCurrency(item.paid_amount) }}</span>
				</span>
			</template>
			<template v-slot:item.unallocated_amount="{ item }">
				<span class="text-primary posa-price-line">
					<span class="currency-symbol">{{ currencySymbol(item.currency) }}</span>
					<span class="amount-value">{{ formatCurrency(item.unallocated_amount) }}</span>
				</span>
			</template>
		</v-data-table>
		<v-divider></v-divider>
	</div>
</template>

<script setup>
import { computed } from "vue";

const __ = (text) => (window.__ ? window.__(text) : text);

const props = defineProps({
	payments: Array,
	selectedPayments: Array,
	posProfile: Object,
	totalUnallocated: Number,
	totalSelected: Number,
	loading: Boolean,
	headers: Array,
	sectionTitle: String,
	currencySymbol: Function,
	formatCurrency: Function,
	paymentRowClass: Function,
});

const emit = defineEmits(["update:selectedPayments"]);

const internalSelectedPayments = computed({
	get: () => props.selectedPayments,
	set: (val) => emit("update:selectedPayments", val),
});

const resolvedSectionTitle = computed(() => props.sectionTitle || __("Payments"));

const paymentRowProps = ({ item }) => {
	if (!props.paymentRowClass) {
		return {};
	}
	const rowClass = props.paymentRowClass(item);
	return rowClass ? { class: rowClass } : {};
};
</script>
