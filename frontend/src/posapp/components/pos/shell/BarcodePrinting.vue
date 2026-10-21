<template>
	<div
		class="pa-0 h-100 barcode-printing-page"
		:class="{ 'barcode-printing-page--mobile': isMobileLayout }"
	>
		<div v-if="isMobileLayout" class="barcode-mobile-header">
			<div class="barcode-mobile-header__copy">
				<span class="barcode-mobile-header__title">{{ __("Barcode Printing") }}</span>
				<span class="barcode-mobile-header__meta">
					{{ mobilePane === "items" ? __("Select barcode items") : __("Review and print labels") }}
				</span>
			</div>
			<v-btn-toggle
				v-model="mobilePane"
				mandatory
				density="compact"
				divided
				class="barcode-mobile-tabs"
			>
				<v-btn value="items" size="small" class="text-none">
					<v-icon start size="18">mdi-magnify</v-icon>
					<span>{{ __("Items") }}</span>
				</v-btn>
				<v-btn value="workspace" size="small" class="text-none">
					<v-icon start size="18">mdi-printer-outline</v-icon>
					<span>{{ __("Print") }}</span>
					<span v-if="totalLabelCount" class="barcode-mobile-tab-count">
						{{ totalLabelCount }}
					</span>
				</v-btn>
			</v-btn-toggle>
		</div>

		<v-row class="h-100 ma-0">
			<!-- Left Column: Item Selector -->
			<v-col
				cols="12"
				md="5"
				class="h-100 pa-0 border-e d-flex flex-column barcode-pane-col barcode-pane-col--items"
				:class="{ 'barcode-pane-hidden': isMobileLayout && mobilePane !== 'items' }"
			>
				<ItemsSelector
					context="barcode"
					:showOnlyBarcodeItems="true"
					class="flex-grow-1"
					@add-item="onAddItem"
					@add-items="onAddItems"
				/>
			</v-col>

			<!-- Right Column: Barcode Printing -->
			<v-col
				cols="12"
				md="7"
				class="h-100 pa-0 barcode-pane-col barcode-pane-col--workspace"
				:class="{ 'barcode-pane-hidden': isMobileLayout && mobilePane !== 'workspace' }"
			>
				<v-card class="h-100 d-flex flex-column pos-themed-card" flat>
					<v-card-title
						class="py-2 px-4 bg-primary text-white d-flex align-center barcode-workspace-title"
					>
						<span class="text-h6 barcode-workspace-title__text">{{
							__("Barcode Label Printing")
						}}</span>
						<v-spacer></v-spacer>
						<v-btn-toggle
							v-model="viewMode"
							mandatory
							density="compact"
							color="white"
							variant="text"
							divided
							class="barcode-view-toggle"
						>
							<v-btn value="labels" size="small" class="text-none" :aria-label="__('Labels')">
								<v-icon start>mdi-format-list-bulleted</v-icon>
								<span class="d-none d-sm-inline">{{ __("Labels") }}</span>
							</v-btn>
							<v-btn
								value="designer"
								size="small"
								class="text-none"
								:aria-label="__('Designer')"
							>
								<v-icon start>mdi-drag-variant</v-icon>
								<span class="d-none d-sm-inline">{{ __("Designer") }}</span>
							</v-btn>
						</v-btn-toggle>
						<template v-if="!isMobileLayout">
							<v-btn
								icon="mdi-truck-delivery"
								variant="text"
								color="white"
								@click="ssccDialog = true"
								:title="__('Generate SSCC-18 Shipping Labels')"
								:aria-label="__('Generate SSCC-18 shipping labels')"
							></v-btn>
							<v-btn
								icon="mdi-verified"
								variant="text"
								color="white"
								@click="verificationDialog = true"
								:title="__('Barcode Verification')"
								:aria-label="__('Verify printed barcodes')"
							></v-btn>
							<v-menu>
								<template v-slot:activator="{ props }">
									<v-btn
										v-bind="props"
										icon="mdi-download"
										variant="text"
										color="white"
										:title="__('Export labels')"
										:aria-label="__('Export labels')"
									></v-btn>
								</template>
								<v-list density="compact">
									<v-list-item @click="onExportPng" :disabled="!items.length">
										<template v-slot:prepend><v-icon>mdi-image</v-icon></template>
										<v-list-item-title>{{ __("PNG") }}</v-list-item-title>
										<v-list-item-subtitle>{{
											__("Render labels as PNG image")
										}}</v-list-item-subtitle>
									</v-list-item>
									<v-list-item @click="onExportSvg" :disabled="!items.length">
										<template v-slot:prepend><v-icon>mdi-svg</v-icon></template>
										<v-list-item-title>{{ __("SVG") }}</v-list-item-title>
										<v-list-item-subtitle>{{
											__("Export as SVG with embedded barcodes")
										}}</v-list-item-subtitle>
									</v-list-item>
									<v-list-item @click="onExportCsv" :disabled="!items.length">
										<template v-slot:prepend
											><v-icon>mdi-file-delimited</v-icon></template
										>
										<v-list-item-title>{{ __("CSV") }}</v-list-item-title>
										<v-list-item-subtitle>{{
											__("Item data as spreadsheet")
										}}</v-list-item-subtitle>
									</v-list-item>
								</v-list>
							</v-menu>
							<v-btn
								icon="mdi-package-variant-closed"
								variant="text"
								color="white"
								@click="importDialog = true"
								:title="__('Import from Document')"
								:aria-label="__('Import items from Sales Order, Delivery Note or BOM')"
							></v-btn>
							<v-btn
								icon="mdi-upload"
								variant="text"
								color="white"
								@click="bulkImportDialog = true"
								:title="__('Bulk Import')"
								:aria-label="__('Bulk import barcode items')"
							></v-btn>
							<v-btn
								icon="mdi-delete"
								variant="text"
								color="white"
								@click="clearAll"
								:title="__('Clear All')"
								:aria-label="__('Clear all barcode items')"
							></v-btn>
						</template>
						<v-menu v-else location="bottom end">
							<template v-slot:activator="{ props }">
								<v-btn
									v-bind="props"
									icon="mdi-dots-vertical"
									variant="text"
									color="white"
									:aria-label="__('More barcode printing actions')"
								></v-btn>
							</template>
							<v-list density="compact">
								<v-list-item
									prepend-icon="mdi-truck-delivery"
									:title="__('SSCC-18 labels')"
									@click="ssccDialog = true"
								></v-list-item>
								<v-list-item
									prepend-icon="mdi-verified"
									:title="__('Barcode verification')"
									@click="verificationDialog = true"
								></v-list-item>
								<v-divider></v-divider>
								<v-list-subheader>{{ __("Export") }}</v-list-subheader>
								<v-list-item
									prepend-icon="mdi-image"
									:title="__('PNG')"
									:disabled="!items.length"
									@click="onExportPng"
								></v-list-item>
								<v-list-item
									prepend-icon="mdi-svg"
									:title="__('SVG')"
									:disabled="!items.length"
									@click="onExportSvg"
								></v-list-item>
								<v-list-item
									prepend-icon="mdi-file-delimited"
									:title="__('CSV')"
									:disabled="!items.length"
									@click="onExportCsv"
								></v-list-item>
								<v-divider></v-divider>
								<v-list-item
									prepend-icon="mdi-package-variant-closed"
									:title="__('Import from document')"
									@click="importDialog = true"
								></v-list-item>
								<v-list-item
									prepend-icon="mdi-upload"
									:title="__('Bulk import')"
									@click="bulkImportDialog = true"
								></v-list-item>
								<v-list-item
									prepend-icon="mdi-delete"
									:title="__('Clear all')"
									:disabled="!items.length"
									@click="clearAll"
								></v-list-item>
							</v-list>
						</v-menu>
					</v-card-title>

					<v-card-text
						v-if="viewMode === 'labels'"
						class="flex-grow-1 overflow-y-auto pa-4 barcode-labels-body"
					>
						<div v-if="isMobileLayout" class="barcode-mobile-setup">
							<div class="barcode-mobile-setup__copy">
								<span class="barcode-mobile-setup__eyebrow">{{ __("Label setup") }}</span>
								<div class="barcode-mobile-setup__chips">
									<v-chip size="x-small" variant="tonal" color="primary">
										{{ pageFormatSummary }}
									</v-chip>
									<v-chip size="x-small" variant="tonal">
										{{ symbology }}
									</v-chip>
									<v-chip size="x-small" variant="tonal">
										{{ outputFormat.toUpperCase() }} · {{ printerDpi }} DPI
									</v-chip>
								</div>
							</div>
							<v-btn
								size="small"
								variant="outlined"
								:prepend-icon="mobileSettingsOpen ? 'mdi-chevron-up' : 'mdi-tune'"
								@click="mobileSettingsOpen = !mobileSettingsOpen"
							>
								{{ mobileSettingsOpen ? __("Hide") : __("Setup") }}
							</v-btn>
						</div>

						<div v-show="!isMobileLayout || mobileSettingsOpen" class="barcode-settings-block">
							<!-- Configuration -->
							<v-row dense class="mb-2 align-center barcode-config-row">
								<v-col cols="6" md="2">
									<v-select
										v-model="pageFormat"
										:items="PAGE_FORMAT_PRESETS"
										:label="__('Page Format')"
										item-title="label"
										item-value="value"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
									></v-select>
								</v-col>
								<v-col v-if="pageFormat === 'A4'" cols="6" md="1">
									<v-text-field
										v-model.number="gridCols"
										:label="__('Cols')"
										type="number"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
										min="1"
									></v-text-field>
								</v-col>
								<v-col v-if="pageFormat === 'A4'" cols="6" md="1">
									<v-text-field
										v-model.number="gridRows"
										:label="__('Rows')"
										type="number"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
										min="1"
									></v-text-field>
								</v-col>
								<v-col cols="6" md="2">
									<v-select
										v-model="symbology"
										:items="symbologyOptions"
										:label="__('Symbology')"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
									></v-select>
								</v-col>
								<v-col cols="6" md="1">
									<v-select
										v-model="outputFormat"
										:items="['html', 'zpl', 'epl']"
										:label="__('Output')"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
									></v-select>
								</v-col>
								<v-col cols="6" md="1">
									<v-select
										v-model="printerDpi"
										:items="[
											{ title: '96 DPI (Browser)', value: 96 },
											{ title: '203 DPI (Thermal)', value: 203 },
											{ title: '300 DPI (High)', value: 300 },
										]"
										:label="__('DPI')"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
									></v-select>
								</v-col>
								<v-col
									v-if="!isMobileLayout"
									cols="12"
									md="4"
									class="d-flex gap-2 flex-wrap barcode-config-actions"
								>
									<v-tooltip :text="__('Preview labels before printing')" location="top">
										<template v-slot:activator="{ props }">
											<v-btn
												v-bind="props"
												color="info"
												variant="text"
												height="40"
												@click="openPreview"
												:disabled="!items.length"
											>
												<v-icon>mdi-eye</v-icon>
											</v-btn>
										</template>
									</v-tooltip>
									<v-btn
										color="secondary"
										class="flex-grow-1 mr-1"
										height="40"
										@click="downloadPdf(items)"
										:disabled="!items.length"
									>
										<v-icon start class="mr-2">mdi-file-pdf-box</v-icon>
										{{ __("PDF") }}
									</v-btn>
									<v-btn
										color="primary"
										class="flex-grow-1 ml-1"
										height="40"
										@click="printLabels(items)"
										:disabled="!items.length"
									>
										<v-icon start class="mr-2">mdi-printer</v-icon>
										{{ __("Print") }}
									</v-btn>
									<v-tooltip :text="__('Print via QZ Tray thermal printer')" location="top">
										<template v-slot:activator="{ props }">
											<v-btn
												v-bind="props"
												color="deep-purple-accent-3"
												class="flex-grow-1 ml-1"
												height="40"
												@click="thermalPrint"
												:disabled="!items.length || !qzThermalAvailable"
												:loading="thermalPrinting"
											>
												<v-icon start class="mr-2">mdi-fire</v-icon>
												{{ __("Thermal") }}
											</v-btn>
										</template>
									</v-tooltip>
								</v-col>
							</v-row>

							<v-row dense class="mb-2 barcode-option-row">
								<v-col cols="6" md="4">
									<v-checkbox
										v-model="includePrice"
										:label="__('Include Price')"
										density="compact"
										hide-details
										color="primary"
									></v-checkbox>
								</v-col>
								<v-col cols="6" md="2">
									<v-checkbox
										v-model="serializationEnabled"
										:label="__('Serialization')"
										density="compact"
										hide-details
										color="primary"
									></v-checkbox>
								</v-col>
								<v-col cols="6" md="2">
									<v-checkbox
										v-model="rfidEnabled"
										:label="__('RFID Encode')"
										density="compact"
										hide-details
										color="primary"
										:disabled="outputFormat !== 'zpl'"
									></v-checkbox>
								</v-col>
								<v-col cols="12" md="2" v-if="rfidEnabled">
									<v-text-field
										v-model="rfidEpcPrefix"
										:label="__('EPC Prefix (Hex)')"
										density="compact"
										variant="outlined"
										hide-details
										class="pos-themed-input"
										placeholder="303402B4DD"
									></v-text-field>
								</v-col>
								<v-col cols="6" md="2">
									<v-checkbox
										v-model="includeBatchSerial"
										:label="__('Include Batch / Serial')"
										density="compact"
										hide-details
										color="primary"
									></v-checkbox>
								</v-col>
								<v-col cols="6" md="4">
									<v-checkbox
										v-model="includeWarehouseLocation"
										:label="__('Include Warehouse Location')"
										density="compact"
										hide-details
										color="primary"
									></v-checkbox>
								</v-col>
							</v-row>
						</div>

						<v-alert
							v-if="sizeWarnings.length"
							type="warning"
							density="compact"
							variant="tonal"
							class="mb-2"
						>
							{{ sizeWarnings[0] }}
						</v-alert>

						<v-alert
							v-if="hasActiveTemplate"
							type="info"
							density="compact"
							variant="tonal"
							class="mb-2 barcode-template-alert"
							closable
							@click:close="clearDesignerTemplate"
						>
							<div class="d-flex align-center barcode-template-alert__body">
								<v-icon start>mdi-ruler-square</v-icon>
								<span>{{
									__("Designer template active — labels render from canvas layout")
								}}</span>
								<v-btn
									variant="text"
									size="small"
									color="primary"
									class="ml-2 text-none"
									@click="viewMode = 'designer'"
								>
									{{ __("Edit Template") }}
								</v-btn>
								<v-btn
									variant="text"
									size="small"
									color="error"
									class="ml-1 text-none"
									@click="clearDesignerTemplate"
								>
									{{ __("Clear") }}
								</v-btn>
							</div>
						</v-alert>

						<v-divider class="my-3"></v-divider>

						<!-- Items List -->
						<v-data-table
							v-if="!isMobileLayout"
							:headers="headers"
							:items="items"
							density="compact"
							class="elevation-1 border rounded"
							:items-per-page="-1"
							hide-default-footer
						>
							<template v-slot:item.uom="{ item }">
								<v-select
									v-if="getItemUomOptions(item).length"
									v-model="item.uom"
									:items="getItemUomOptions(item)"
									density="compact"
									variant="outlined"
									hide-details
									class="pos-themed-input"
									@update:modelValue="onItemUomChange(item)"
								></v-select>
								<span v-else class="text-caption text-medium-emphasis">-</span>
							</template>
							<template v-slot:item.price="{ item }">
								<span class="text-caption">{{ formatCurrency(item.price) }}</span>
							</template>
							<template v-slot:item.qty="{ item }">
								<div class="pos-table__qty-counter">
									<v-btn
										size="small"
										variant="flat"
										class="pos-table__qty-btn pos-table__qty-btn--minus minus-btn qty-control-btn"
										@click="decrementQty(item)"
										:aria-label="__('Decrease quantity')"
									>
										<v-icon size="small">mdi-minus</v-icon>
									</v-btn>
									<div
										v-if="!item._editingQty"
										class="pos-table__qty-display amount-value"
										@click="openQtyEdit(item)"
										tabindex="0"
										role="button"
										:aria-label="__('Edit quantity')"
									>
										{{ item.qty }}
									</div>
									<v-text-field
										v-else
										v-model="editingQtyValue"
										density="compact"
										variant="outlined"
										class="pos-table__qty-input"
										@blur="closeQtyEdit(item)"
										@keydown.enter.prevent="closeQtyEdit(item)"
										@click.stop
										:id="'qty-input-' + item._row_id"
										:autofocus="true"
										type="number"
										hide-details
									></v-text-field>
									<v-btn
										size="small"
										variant="flat"
										class="pos-table__qty-btn pos-table__qty-btn--plus plus-btn qty-control-btn"
										@click="incrementQty(item)"
										:aria-label="__('Increase quantity')"
									>
										<v-icon size="small">mdi-plus</v-icon>
									</v-btn>
								</div>
							</template>
							<template v-slot:item.barcode="{ item }">
								<div v-if="item.barcode" class="d-flex align-center ga-1">
									<template v-if="getAvailableBarcodes(item).length > 1">
										<v-select
											v-model="item.barcode"
											:items="getAvailableBarcodes(item)"
											item-title="barcode"
											item-value="barcode"
											density="compact"
											variant="outlined"
											hide-details
											class="pos-themed-input"
											@update:modelValue="(v) => selectBarcode(item, v)"
										>
											<template v-slot:item="{ props, item: bcItem }">
												<v-list-item
													v-bind="props"
													:subtitle="bcItem.raw.barcode_type || ''"
												></v-list-item>
											</template>
										</v-select>
									</template>
									<span v-else class="text-caption">
										{{ item.barcode }}
										<v-chip
											v-if="getBarcodeTypeLabel(item)"
											size="x-small"
											variant="outlined"
											class="ml-1"
											>{{ getBarcodeTypeLabel(item) }}</v-chip
										>
									</span>
									<v-tooltip v-if="validateBarcodeItem(item)" location="top">
										<template v-slot:activator="{ props }">
											<v-icon v-bind="props" color="error" size="small"
												>mdi-alert-circle</v-icon
											>
										</template>
										<span>{{ validateBarcodeItem(item) }}</span>
									</v-tooltip>
								</div>
								<div v-else class="text-error text-caption">{{ __("No Barcode") }}</div>
							</template>
							<template v-slot:item.grams="{ item }">
								<v-text-field
									v-if="shouldShowScaleGramsInput(item)"
									v-model.number="item.scale_grams"
									density="compact"
									variant="outlined"
									hide-details
									type="number"
									min="1"
									step="1"
									class="pos-themed-input"
									@blur="onItemScaleGramsChange(item)"
									@keydown.enter.prevent="onItemScaleGramsChange(item)"
								></v-text-field>
								<span v-else class="text-caption text-medium-emphasis">-</span>
							</template>
							<template v-slot:item.warehouseLocation="{ item }">
								<v-autocomplete
									v-model="item.warehouseLocation"
									:items="warehouseOptions"
									item-title="warehouse_name"
									item-value="name"
									density="compact"
									variant="outlined"
									hide-details
									class="pos-themed-input"
									:placeholder="__('Loc')"
									clearable
								></v-autocomplete>
							</template>
							<template v-slot:item.variableData="{ item }">
								<v-btn
									icon="mdi-variable"
									size="small"
									variant="text"
									color="primary"
									@click="openVariableDataDialog(item)"
									:aria-label="__('Variable data')"
								></v-btn>
							</template>
							<template v-slot:item.actions="{ item }">
								<v-btn
									icon="mdi-delete"
									size="small"
									variant="text"
									color="error"
									@click="removeItem(item)"
									:aria-label="__('Remove barcode item')"
								></v-btn>
							</template>
						</v-data-table>

						<div v-if="isMobileLayout" class="barcode-mobile-queue">
							<div class="barcode-mobile-queue__header">
								<div>
									<span class="barcode-mobile-queue__eyebrow">{{ __("Print queue") }}</span>
									<strong>
										{{
											totalLabelCount === 1
												? __("1 label")
												: __("{0} labels", [String(totalLabelCount)])
										}}
									</strong>
								</div>
								<v-btn
									v-if="items.length"
									size="small"
									variant="text"
									color="error"
									prepend-icon="mdi-delete-outline"
									@click="clearAll"
								>
									{{ __("Clear") }}
								</v-btn>
							</div>

							<div v-if="!items.length" class="barcode-mobile-queue__empty">
								<v-icon size="42" color="medium-emphasis">mdi-barcode-off</v-icon>
								<strong>{{ __("No labels queued") }}</strong>
								<span>{{ __("Switch to Items and add products with barcodes.") }}</span>
								<v-btn
									color="primary"
									variant="tonal"
									prepend-icon="mdi-magnify"
									@click="mobilePane = 'items'"
								>
									{{ __("Browse items") }}
								</v-btn>
							</div>

							<div v-else class="barcode-mobile-queue__list">
								<article
									v-for="item in items"
									:key="item._row_id || item.item_code"
									class="barcode-queue-card"
								>
									<div class="barcode-queue-card__head">
										<div class="barcode-queue-card__identity">
											<strong>{{ item.item_name || item.item_code }}</strong>
											<span>{{ item.item_code }}</span>
										</div>
										<v-btn
											icon="mdi-delete-outline"
											size="small"
											variant="text"
											color="error"
											:aria-label="__('Remove barcode item')"
											@click="removeItem(item)"
										></v-btn>
									</div>

									<div class="barcode-queue-card__barcode">
										<v-icon size="18" color="primary">mdi-barcode</v-icon>
										<template v-if="item.barcode">
											<v-select
												v-if="getAvailableBarcodes(item).length > 1"
												v-model="item.barcode"
												:items="getAvailableBarcodes(item)"
												item-title="barcode"
												item-value="barcode"
												density="compact"
												variant="outlined"
												hide-details
												class="pos-themed-input barcode-queue-card__barcode-select"
												@update:modelValue="(v) => selectBarcode(item, v)"
											>
												<template v-slot:item="{ props, item: bcItem }">
													<v-list-item
														v-bind="props"
														:subtitle="bcItem.raw.barcode_type || ''"
													></v-list-item>
												</template>
											</v-select>
											<span v-else class="barcode-queue-card__barcode-value">
												{{ item.barcode }}
											</span>
											<v-chip
												v-if="getBarcodeTypeLabel(item)"
												size="x-small"
												variant="outlined"
											>
												{{ getBarcodeTypeLabel(item) }}
											</v-chip>
											<v-tooltip v-if="validateBarcodeItem(item)" location="top">
												<template v-slot:activator="{ props }">
													<v-icon v-bind="props" color="error" size="small"
														>mdi-alert-circle</v-icon
													>
												</template>
												<span>{{ validateBarcodeItem(item) }}</span>
											</v-tooltip>
										</template>
										<span v-else class="text-error text-caption">{{
											__("No Barcode")
										}}</span>
									</div>

									<div class="barcode-queue-card__fields">
										<div class="barcode-queue-card__metric">
											<span>{{ __("Price") }}</span>
											<strong>{{ formatCurrency(item.price) }}</strong>
										</div>

										<v-select
											v-if="getItemUomOptions(item).length"
											v-model="item.uom"
											:items="getItemUomOptions(item)"
											label="UOM"
											density="compact"
											variant="outlined"
											hide-details
											class="pos-themed-input barcode-queue-card__uom"
											@update:modelValue="onItemUomChange(item)"
										></v-select>

										<div
											class="barcode-queue-card__metric barcode-queue-card__metric--qty"
										>
											<span>{{ __("Quantity") }}</span>
											<div class="pos-table__qty-counter">
												<v-btn
													size="small"
													variant="flat"
													class="pos-table__qty-btn pos-table__qty-btn--minus minus-btn qty-control-btn"
													@click="decrementQty(item)"
													:aria-label="__('Decrease quantity')"
												>
													<v-icon size="small">mdi-minus</v-icon>
												</v-btn>
												<div
													v-if="!item._editingQty"
													class="pos-table__qty-display amount-value"
													@click="openQtyEdit(item)"
													tabindex="0"
													role="button"
													:aria-label="__('Edit quantity')"
												>
													{{ item.qty }}
												</div>
												<v-text-field
													v-else
													v-model="editingQtyValue"
													density="compact"
													variant="outlined"
													class="pos-table__qty-input"
													@blur="closeQtyEdit(item)"
													@keydown.enter.prevent="closeQtyEdit(item)"
													@click.stop
													:id="'qty-input-' + item._row_id"
													:autofocus="true"
													type="number"
													hide-details
												></v-text-field>
												<v-btn
													size="small"
													variant="flat"
													class="pos-table__qty-btn pos-table__qty-btn--plus plus-btn qty-control-btn"
													@click="incrementQty(item)"
													:aria-label="__('Increase quantity')"
												>
													<v-icon size="small">mdi-plus</v-icon>
												</v-btn>
											</div>
										</div>

										<v-text-field
											v-if="shouldShowScaleGramsInput(item)"
											v-model.number="item.scale_grams"
											:label="__('Weight (g)')"
											density="compact"
											variant="outlined"
											hide-details
											type="number"
											min="1"
											step="1"
											class="pos-themed-input barcode-queue-card__weight"
											@blur="onItemScaleGramsChange(item)"
											@keydown.enter.prevent="onItemScaleGramsChange(item)"
										></v-text-field>

										<v-autocomplete
											v-if="includeWarehouseLocation"
											v-model="item.warehouseLocation"
											:items="warehouseOptions"
											item-title="warehouse_name"
											item-value="name"
											:label="__('Location')"
											density="compact"
											variant="outlined"
											hide-details
											class="pos-themed-input barcode-queue-card__location"
											clearable
										></v-autocomplete>
									</div>

									<div class="barcode-queue-card__footer">
										<v-btn
											size="small"
											variant="text"
											color="primary"
											prepend-icon="mdi-variable"
											@click="openVariableDataDialog(item)"
										>
											{{ __("Variable data") }}
										</v-btn>
									</div>
								</article>
							</div>
						</div>
					</v-card-text>

					<v-card-text v-else class="flex-grow-1 pa-0 d-flex flex-column overflow-hidden">
						<div class="d-flex flex-grow-1 barcode-designer-body" style="min-height: 0">
							<div class="flex-grow-1 overflow-hidden barcode-designer-canvas">
								<LabelDesigner
									:designer="designer"
									@select="(id) => designer.selectObject(id)"
									@dblclick="() => {}"
								/>
							</div>
							<div class="barcode-designer-panel" style="width: 260px; flex-shrink: 0">
								<LabelDesignerPanel
									:object="designer.selectedObject.value"
									@change="onDesignerObjectChange"
									@uploadImage="onUploadImage"
								/>
							</div>
						</div>
						<div
							class="d-flex justify-space-between pa-2 ga-2 border-t align-center barcode-designer-actions"
						>
							<div class="d-flex ga-2 barcode-designer-actions__group">
								<v-btn variant="text" @click="viewMode = 'labels'">
									<v-icon start>mdi-arrow-left</v-icon>
									{{ __("Back to Labels") }}
								</v-btn>
								<v-btn
									variant="outlined"
									prepend-icon="mdi-upload"
									@click="importDesignerLayout"
								>
									{{ __("Import Layout") }}
								</v-btn>
							</div>
							<div class="d-flex ga-2 barcode-designer-actions__group">
								<v-btn
									color="primary"
									variant="outlined"
									prepend-icon="mdi-content-save-outline"
									@click="saveTemplateDialog = true"
								>
									{{ __("Save Template") }}
								</v-btn>
								<v-btn
									color="primary"
									variant="outlined"
									prepend-icon="mdi-folder-open-outline"
									@click="templateLibraryDialog = true"
								>
									{{ __("Load Template") }}
								</v-btn>
								<v-btn
									color="success"
									variant="flat"
									prepend-icon="mdi-check"
									@click="applyDesignerTemplate"
								>
									<v-badge v-if="hasActiveTemplate" dot color="warning" inline></v-badge>
									{{ hasActiveTemplate ? __("Update Template") : __("Use as Template") }}
								</v-btn>
								<v-btn
									color="primary"
									variant="outlined"
									prepend-icon="mdi-content-save"
									@click="exportDesignerLayout"
								>
									{{ __("Export") }}
								</v-btn>
							</div>
						</div>
					</v-card-text>

					<div v-if="isMobileLayout && viewMode === 'labels'" class="barcode-mobile-printbar">
						<v-btn variant="text" color="info" :disabled="!items.length" @click="openPreview">
							<v-icon size="20">mdi-eye-outline</v-icon>
							<span>{{ __("Preview") }}</span>
						</v-btn>
						<v-btn
							variant="tonal"
							color="secondary"
							:disabled="!items.length"
							@click="downloadPdf(items)"
						>
							<v-icon size="20">mdi-file-pdf-box</v-icon>
							<span>{{ __("PDF") }}</span>
						</v-btn>
						<v-btn
							variant="flat"
							color="primary"
							:disabled="!items.length"
							@click="printLabels(items)"
						>
							<v-icon size="20">mdi-printer</v-icon>
							<span>{{ __("Print") }}</span>
						</v-btn>
						<v-btn
							variant="text"
							color="deep-purple-accent-3"
							:disabled="!items.length || !qzThermalAvailable"
							:loading="thermalPrinting"
							@click="thermalPrint"
						>
							<v-icon size="20">mdi-fire</v-icon>
							<span>{{ __("Thermal") }}</span>
						</v-btn>
					</div>
				</v-card>
			</v-col>
		</v-row>

		<div v-if="isMobileLayout && mobilePane === 'items'" class="barcode-mobile-items-bar">
			<v-btn block color="primary" size="large" @click="mobilePane = 'workspace'">
				<v-icon start>mdi-printer-outline</v-icon>
				<span>{{ __("Review print queue") }}</span>
				<span v-if="totalLabelCount" class="barcode-mobile-items-bar__count">
					{{ totalLabelCount }}
				</span>
			</v-btn>
		</div>

		<!-- Save Template Dialog -->
		<v-dialog v-model="saveTemplateDialog" max-width="450" :fullscreen="isMobileLayout">
			<v-card>
				<v-card-title class="bg-primary text-white">{{ __("Save Label Template") }}</v-card-title>
				<v-card-text class="pt-4">
					<v-text-field
						v-model="saveTemplateTitle"
						:label="__('Template Title')"
						variant="outlined"
						density="compact"
						class="mb-3"
						autofocus
					></v-text-field>
					<v-textarea
						v-model="saveTemplateDescription"
						:label="__('Description (optional)')"
						variant="outlined"
						density="compact"
						rows="2"
						class="mb-3"
					></v-textarea>
				</v-card-text>
				<v-card-actions class="justify-end pa-4 pt-0">
					<v-btn variant="text" @click="saveTemplateDialog = false">{{ __("Cancel") }}</v-btn>
					<v-btn
						color="primary"
						variant="elevated"
						:loading="saveTemplateLoading"
						@click="onSaveTemplate"
						>{{ __("Save") }}</v-btn
					>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<!-- Template Library Dialog -->
		<TemplateLibrary v-model="templateLibraryDialog" @load="loadTemplateFromLibrary" />

		<!-- Barcode Verification Dialog -->
		<VerificationDialog v-model="verificationDialog" />

		<!-- Add Item Quantity Dialog -->
		<v-dialog v-model="addItemDialog" max-width="400">
			<v-card v-if="pendingAddItem">
				<v-card-title class="bg-primary text-white">
					{{ __("Enter Quantity") }}
				</v-card-title>
				<v-card-text class="pt-4">
					<div class="text-subtitle-1 mb-2">{{ pendingAddItem.item_name }}</div>
					<div
						v-if="pendingAddItem && shouldShowScaleGramsInput(pendingAddItem)"
						class="text-caption text-medium-emphasis mb-2"
					>
						{{ __("Scale barcode detected. Quantity here is the number of labels to print.") }}
					</div>
					<v-select
						v-if="pendingAddItem && getItemUomOptions(pendingAddItem).length > 1"
						v-model="pendingAddItem.uom"
						:items="getItemUomOptions(pendingAddItem)"
						:label="__('UOM')"
						variant="outlined"
						density="compact"
						class="mb-2 pos-themed-input"
						@update:modelValue="onPendingUomChange"
					></v-select>
					<v-text-field
						v-model.number="addItemQty"
						:label="
							pendingAddItem && shouldShowScaleGramsInput(pendingAddItem)
								? __('Labels')
								: __('Quantity')
						"
						type="number"
						min="1"
						step="1"
						variant="outlined"
						autofocus
						@keydown.enter="confirmAddItem"
					></v-text-field>
					<v-text-field
						v-if="pendingAddItem && shouldShowScaleGramsInput(pendingAddItem)"
						v-model.number="pendingScaleGrams"
						:label="__('Weight (grams)')"
						type="number"
						min="1"
						step="1"
						variant="outlined"
						class="mt-2"
						@update:modelValue="onPendingScaleGramsInput"
						@blur="syncPendingScaleBarcode"
						@keydown.enter.prevent="syncPendingScaleBarcode"
					></v-text-field>
					<div
						v-if="
							pendingAddItem &&
							shouldShowScaleGramsInput(pendingAddItem) &&
							pendingAddItem.barcode
						"
						class="text-caption text-medium-emphasis mt-1"
					>
						{{ __("Generated scale barcode: {0}", [pendingAddItem.barcode]) }}
					</div>
				</v-card-text>
				<v-card-actions class="justify-end">
					<v-btn variant="text" @click="closeAddItemDialog">{{ __("Cancel") }}</v-btn>
					<v-btn color="primary" variant="elevated" @click="confirmAddItem">{{ __("Add") }}</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
		<!-- Variable Data Dialog -->
		<v-dialog v-model="variableDataDialog" max-width="400" :fullscreen="isMobileLayout">
			<v-card v-if="variableDataItem">
				<v-card-title class="bg-primary text-white">
					{{ __("Variable Data") }}
				</v-card-title>
				<v-card-text class="pt-4">
					<v-autocomplete
						v-if="getAvailableBatches(variableDataItem).length"
						v-model="variableDataItem.batch_no"
						:items="getAvailableBatches(variableDataItem)"
						item-title="batch_no"
						item-value="batch_no"
						:label="__('Batch No')"
						variant="outlined"
						density="compact"
						class="mb-2"
						clearable
						@update:modelValue="onSelectBatch(variableDataItem, $event)"
					></v-autocomplete>
					<v-text-field
						v-else
						v-model="variableDataItem.batch_no"
						:label="__('Batch No')"
						variant="outlined"
						density="compact"
						class="mb-2"
					></v-text-field>
					<v-autocomplete
						v-if="getAvailableSerials(variableDataItem).length"
						v-model="variableDataItem.serial_no"
						:items="getAvailableSerials(variableDataItem)"
						item-title="serial_no"
						item-value="serial_no"
						:label="__('Serial No')"
						:hint="__('e.g. 1001-1050')"
						persistent-hint
						variant="outlined"
						density="compact"
						class="mb-2"
						clearable
						@update:modelValue="onSelectSerial(variableDataItem, $event)"
					></v-autocomplete>
					<v-text-field
						v-else
						v-model="variableDataItem.serial_no"
						:label="__('Serial No')"
						:hint="__('e.g. 1001-1050')"
						persistent-hint
						variant="outlined"
						density="compact"
						class="mb-2"
					></v-text-field>
					<v-text-field
						v-model="variableDataItem.expiry_date"
						:label="__('Expiry Date')"
						:hint="__('Auto-filled when batch selected')"
						persistent-hint
						type="date"
						variant="outlined"
						density="compact"
						class="mb-2"
					></v-text-field>
					<v-autocomplete
						v-model="variableDataItem.warehouseLocation"
						:items="warehouseOptions"
						item-title="warehouse_name"
						item-value="name"
						:label="__('Location')"
						:loading="warehouseLoading"
						hint="__('Choose warehouse from ERPNext')"
						persistent-hint
						variant="outlined"
						density="compact"
						class="mb-2"
						clearable
					></v-autocomplete>
				</v-card-text>
				<v-card-actions class="justify-end">
					<v-btn variant="text" @click="closeVariableDataDialog">{{ __("Cancel") }}</v-btn>
					<v-btn color="primary" variant="elevated" @click="closeVariableDataDialog">{{
						__("Save")
					}}</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
		<!-- Bulk Import Dialog -->
		<v-dialog v-model="bulkImportDialog" max-width="600" :fullscreen="isMobileLayout">
			<v-card>
				<v-card-title class="bg-primary text-white d-flex align-center">
					<span>{{ __("Bulk Import") }}</span>
					<v-spacer></v-spacer>
					<v-btn
						icon="mdi-close"
						variant="text"
						color="white"
						@click="bulkImportDialog = false"
					></v-btn>
				</v-card-title>
				<v-card-text class="pt-4">
					<v-radio-group
						v-model="bulkImportFormat"
						inline
						hide-details
						density="compact"
						class="mb-2"
					>
						<v-radio :label="__('CSV')" value="csv"></v-radio>
						<v-radio :label="__('JSON')" value="json"></v-radio>
					</v-radio-group>
					<v-textarea
						v-model="bulkImportRaw"
						:label="
							bulkImportFormat === 'csv'
								? __('item_code, qty')
								: __('[{item_code:..., qty:...}]')
						"
						variant="outlined"
						rows="6"
						:hint="
							bulkImportFormat === 'csv'
								? __('One per line: item_code, qty')
								: __('Array of objects with item_code, qty')
						"
						persistent-hint
					></v-textarea>
					<v-alert
						v-if="bulkImportError"
						type="error"
						density="compact"
						variant="tonal"
						class="mb-2"
					>
						{{ bulkImportError }}
					</v-alert>
					<v-alert
						v-if="bulkImportSuccess"
						type="success"
						density="compact"
						variant="tonal"
						class="mb-2"
					>
						{{ bulkImportSuccess }}
					</v-alert>
				</v-card-text>
				<v-card-actions class="justify-end">
					<v-btn variant="text" @click="bulkImportDialog = false">{{ __("Cancel") }}</v-btn>
					<v-btn
						color="primary"
						variant="elevated"
						:loading="bulkImporting"
						@click="processBulkImport"
					>
						{{ __("Import") }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<ImportSourceDialog v-model="importDialog" @import="onImportFromSource" />

		<!-- SSCC-18 Shipping Label Generator Dialog -->
		<v-dialog v-model="ssccDialog" max-width="550" :fullscreen="isMobileLayout">
			<v-card>
				<v-card-title class="bg-primary text-white d-flex align-center">
					<span class="text-h6">{{ __("Generate SSCC-18 Shipping Labels") }}</span>
					<v-spacer></v-spacer>
					<v-btn icon="mdi-close" variant="text" color="white" @click="ssccDialog = false"></v-btn>
				</v-card-title>
				<v-card-text class="pt-4">
					<v-row dense>
						<v-col cols="12" md="6">
							<v-text-field
								v-model="ssccCompanyPrefix"
								:label="__('GS1 Company Prefix')"
								variant="outlined"
								density="compact"
								hide-details
								placeholder="1234567"
							></v-text-field>
						</v-col>
						<v-col cols="6" md="3">
							<v-select
								v-model="ssccExtensionDigit"
								:items="['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']"
								:label="__('Extension')"
								variant="outlined"
								density="compact"
								hide-details
							></v-select>
						</v-col>
						<v-col cols="6" md="3">
							<v-text-field
								v-model.number="ssccCount"
								:label="__('Count')"
								type="number"
								min="1"
								max="100"
								variant="outlined"
								density="compact"
								hide-details
							></v-text-field>
						</v-col>
					</v-row>
					<v-row dense class="mt-2">
						<v-col cols="12" md="6">
							<v-text-field
								v-model="ssccDocumentRef"
								:label="__('Delivery Note / Sales Invoice (optional)')"
								variant="outlined"
								density="compact"
								hide-details
								:placeholder="__('e.g. DN-2024-001')"
							></v-text-field>
						</v-col>
						<v-col cols="12" md="6">
							<v-select
								v-model="ssccShipToType"
								:items="[
									{ title: __('Ship to Customer'), value: 'customer' },
									{ title: __('Ship from Company'), value: 'company' },
								]"
								:label="__('Address Source')"
								variant="outlined"
								density="compact"
								hide-details
								item-title="title"
								item-value="value"
							></v-select>
						</v-col>
					</v-row>
					<v-row dense class="mt-2" v-if="ssccGeneratedItems.length">
						<v-col cols="12">
							<v-divider class="mb-2"></v-divider>
							<div class="text-subtitle-2 mb-1">{{ __("Generated SSCC-18 Codes") }}</div>
							<v-list density="compact" class="border rounded">
								<v-list-item
									v-for="(gen, idx) in ssccGeneratedItems"
									:key="idx"
									density="compact"
								>
									<template v-slot:prepend>
										<v-icon color="primary">mdi-barcode</v-icon>
									</template>
									<v-list-item-title class="font-family-mono">{{
										gen.human_readable
									}}</v-list-item-title>
									<v-list-item-subtitle>{{ gen.sscc18 }}</v-list-item-subtitle>
									<template v-slot:append>
										<v-icon color="success" size="small">mdi-check-circle</v-icon>
									</template>
								</v-list-item>
							</v-list>
						</v-col>
					</v-row>
				</v-card-text>
				<v-card-actions
					class="justify-space-between pa-4 pt-0 barcode-dialog-actions barcode-sscc-actions"
				>
					<div class="barcode-dialog-actions__start">
						<v-btn
							v-if="ssccGeneratedItems.length"
							color="success"
							variant="elevated"
							prepend-icon="mdi-plus"
							@click="addSsccToQueue"
							class="mr-2"
						>
							{{ __("Add {0} to Queue", [String(ssccGeneratedItems.length)]) }}
						</v-btn>
					</div>
					<div class="barcode-dialog-actions__end">
						<v-btn variant="text" @click="ssccDialog = false" class="mr-1">{{
							__("Close")
						}}</v-btn>
						<v-btn
							color="primary"
							variant="elevated"
							:loading="ssccGenerating"
							@click="generateSscc"
						>
							<v-icon start>mdi-barcode-scan</v-icon>
							{{ __("Generate") }}
						</v-btn>
					</div>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<!-- Label Preview Dialog -->
		<v-dialog v-model="previewDialog" fullscreen>
			<v-card v-if="previewContent" class="d-flex flex-column barcode-preview-card">
				<v-card-title class="bg-primary text-white d-flex align-center">
					<span class="text-h6">{{ __("Label Preview") }}</span>
					<v-spacer></v-spacer>
					<v-btn
						icon="mdi-close"
						variant="text"
						color="white"
						@click="previewDialog = false"
					></v-btn>
				</v-card-title>
				<v-card-text class="flex-grow-1 pa-0 d-flex flex-column">
					<iframe
						:srcdoc="previewContent"
						class="flex-grow-1 barcode-preview-frame"
						style="width: 100%; border: none"
					></iframe>
				</v-card-text>
				<v-card-actions class="pa-4 justify-center barcode-preview-actions">
					<v-btn color="primary" size="large" prepend-icon="mdi-printer" @click="printFromPreview">
						{{ __("Print") }}
					</v-btn>
					<v-btn
						color="secondary"
						size="large"
						prepend-icon="mdi-file-pdf-box"
						@click="pdfFromPreview"
					>
						{{ __("Download PDF") }}
					</v-btn>
					<v-btn variant="text" size="large" @click="previewDialog = false">
						{{ __("Close") }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted, ref } from "vue";
import { useResponsive } from "../../../composables/core/useResponsive";
import ItemsSelector from "../items/ItemsSelector.vue";
import { useItemsStore } from "../../../stores/itemsStore";
import { useUIStore } from "../../../stores/uiStore";
import { useToastStore } from "../../../stores/toastStore";
import { useBarcodePrintQueue } from "../../../composables/pos/items/useBarcodePrintQueue";
import {
	useBarcodePrintOutput,
	PAGE_FORMAT_PRESETS,
	validateBarcodeItem,
	getBarcodeTypeLabel,
} from "../../../composables/pos/items/useBarcodePrintOutput";
import { useScaleBarcodeSettings } from "../../../composables/pos/items/useScaleBarcodeSettings";
import { useLabelDesigner } from "../../../composables/pos/items/useLabelDesigner";
import { useSsccGenerator } from "../../../composables/pos/items/useSsccGenerator";
import LabelDesigner from "./LabelDesigner.vue";
import LabelDesignerPanel from "./LabelDesignerPanel.vue";
import TemplateLibrary from "./TemplateLibrary.vue";
import VerificationDialog from "./VerificationDialog.vue";
import ImportSourceDialog from "./ImportSourceDialog.vue";
import { exportPng, exportSvg, exportCsv } from "../../../services/exportService";

const itemsStore = useItemsStore();
const uiStore = useUIStore();

const printQueue = useBarcodePrintQueue();
const printOutput = useBarcodePrintOutput();
const scaleSettings = useScaleBarcodeSettings();

const {
	items,
	editingQtyValue,
	addItemDialog,
	addItemQty,
	pendingAddItem,
	pendingScaleGrams,
	addOrMergePrintableItem,
	removeItem,
	clearAll,
	incrementQty,
	decrementQty,
	openQtyEdit,
	closeQtyEdit,
	onAddItem,
	confirmAddItem,
	closeAddItemDialog,
	onPendingUomChange,
	onPendingScaleGramsInput,
	syncPendingScaleBarcode,
	onItemScaleGramsChange,
	onItemUomChange,
	getItemUomOptions,
	getAvailableBarcodes,
	selectBarcode,
	variableDataDialog,
	variableDataItem,
	openVariableDataDialog,
	closeVariableDataDialog,
	warehouseOptions,
	warehouseLoading,
	getAvailableBatches,
	getAvailableSerials,
	onSelectBatch,
	onSelectSerial,
	importItems,
	serializationEngine,
	serializationEnabled,
	cleanup: cleanupQueue,
} = printQueue;

const {
	pageFormat,
	gridCols,
	gridRows,
	includePrice,
	includeBatchSerial,
	includeWarehouseLocation,
	symbology,
	symbologyOptions,
	outputFormat,
	printerDpi,
	getPrintableItems,
	printLabels,
	printLabelsThermalWithFallback,
	printLabelsRawWithFallback,
	qzThermalAvailable,
	downloadPdf,
	getLabelSizeWarnings,
	formatCurrency,
	hasActiveTemplate,
	setDesignerTemplate,
	clearDesignerTemplate,
	rfidEnabled,
	rfidEpcPrefix,
	getEpcData,
} = printOutput;

const thermalPrinting = ref(false);
const importDialog = ref(false);
const bulkImportDialog = ref(false);
const bulkImportRaw = ref("");
const bulkImportFormat = ref("csv");
const bulkImporting = ref(false);
const bulkImportError = ref("");
const bulkImportSuccess = ref("");

const viewMode = ref<"labels" | "designer">("labels");
const designer = useLabelDesigner();

const { windowWidth } = useResponsive();
const isMobileLayout = computed(() => windowWidth.value < 960);
const mobilePane = ref<"items" | "workspace">("items");
const mobileSettingsOpen = ref(false);
const totalLabelCount = computed(() =>
	items.value.reduce((total: number, item: any) => {
		const qty = Math.round(Number(item.qty) || 1);
		return total + Math.max(1, qty);
	}, 0),
);
const pageFormatSummary = computed(
	() => PAGE_FORMAT_PRESETS.find((preset) => preset.value === pageFormat.value)?.label || pageFormat.value,
);

// SSCC-18 generator state
const ssccDialog = ref(false);
const ssccCount = ref(1);
const ssccDocumentRef = ref("");
const ssccShipToType = ref<"customer" | "company">("customer");
const ssccGeneratedItems = ref<Array<{ sscc18: string; human_readable: string; serial_ref: number }>>([]);
const ssccGenerator = useSsccGenerator();
const ssccCompanyPrefix = ssccGenerator.companyPrefix;
const ssccExtensionDigit = ssccGenerator.extensionDigit;
const ssccGenerating = ssccGenerator.generating;

const generateSscc = async () => {
	const count = Math.max(1, Math.min(100, Math.round(ssccCount.value) || 1));
	try {
		const items = await ssccGenerator.generateBatch(count);
		ssccGeneratedItems.value = items;
	} catch {
		useToastStore().show({ title: __("Failed to generate SSCC-18 serials"), color: "error" });
	}
};

const addSsccToQueue = () => {
	for (const gen of ssccGeneratedItems.value) {
		addOrMergePrintableItem(
			{
				item_code: gen.sscc18,
				item_name: `SSCC-18 ${gen.human_readable}`,
				barcode: gen.sscc18,
				qty: 1,
				uom: "",
				_prices_by_uom: {},
				item_barcode: [{ barcode: gen.sscc18, barcode_type: "SSCC-18" }],
				item_uoms: [],
				_symbology: "CODE128",
			},
			1,
			"sscc",
		);
	}
	useToastStore().show({
		title: __("{0} SSCC-18 label(s) added to queue", [String(ssccGeneratedItems.value.length)]),
		color: "success",
	});
	ssccDialog.value = false;
	ssccGeneratedItems.value = [];
};

const onAddItems = async (selectedItems) => {
	for (const item of selectedItems) {
		await onAddItem(item);
	}
};

const processBulkImport = async () => {
	bulkImportError.value = "";
	bulkImportSuccess.value = "";
	const raw = (bulkImportRaw.value || "").trim();
	if (!raw) {
		bulkImportError.value = __("Please enter data to import");
		return;
	}

	bulkImporting.value = true;
	try {
		let entries: Array<{ item_code: string; qty: number }> = [];

		if (bulkImportFormat.value === "csv") {
			const lines = raw.split("\n").filter((l) => l.trim());
			for (const line of lines) {
				const parts = line.split(",").map((p) => p.trim());
				if (parts[0]) {
					entries.push({
						item_code: parts[0],
						qty: parts[1] ? parseInt(parts[1], 10) || 1 : 1,
					});
				}
			}
		} else {
			const parsed = JSON.parse(raw);
			if (!Array.isArray(parsed)) throw new Error("JSON must be an array");
			entries = parsed
				.map((e) => ({
					item_code: String(e.item_code || e.item || "").trim(),
					qty: parseInt(e.qty || e.quantity || "1", 10) || 1,
				}))
				.filter((e) => e.item_code);
		}

		if (!entries.length) {
			bulkImportError.value = __("No valid entries found");
			return;
		}

		const knownItems = itemsStore.items || [];
		let added = 0;
		for (const entry of entries) {
			const found = knownItems.find(
				(i) =>
					i.item_code === entry.item_code ||
					i.name === entry.item_code ||
					i.barcode === entry.item_code,
			);
			if (found) {
				added++;
				const qty = entry.qty || 1;
				addOrMergePrintableItem(
					{
						...found,
						barcode:
							found.barcode ||
							(Array.isArray(found.item_barcode) && found.item_barcode[0]?.barcode) ||
							"",
						uom: found.uom || found.stock_uom || "",
						qty,
						_prices_by_uom: found._prices_by_uom || {},
						item_barcode: found.item_barcode || [],
						item_uoms: found.item_uoms || [],
					},
					qty,
					"bulk-import",
				);
			} else {
				try {
					const res = await frappe.call({
						method: "posawesome.posawesome.api.items.get_items_details",
						args: {
							items_data: JSON.stringify([{ item_code: entry.item_code }]),
							pos_profile: JSON.stringify(uiStore.posProfile || {}),
							price_list: uiStore.posProfile?.selling_price_list || "",
						},
						silent: true,
					});
					const details = res.message && res.message[0];
					if (details) {
						added++;
						const qty = entry.qty || 1;
						addOrMergePrintableItem(
							{
								...details,
								barcode:
									details.barcode ||
									(Array.isArray(details.item_barcode) &&
										details.item_barcode[0]?.barcode) ||
									"",
								uom: details.uom || details.stock_uom || "",
								qty,
								_prices_by_uom: details._prices_by_uom || {},
								item_barcode: details.item_barcode || [],
								item_uoms: details.item_uoms || [],
							},
							qty,
							"bulk-import",
						);
					} else {
						console.warn("Item not found:", entry.item_code);
					}
				} catch (e) {
					console.warn("Failed to fetch item:", entry.item_code, e);
				}
			}
		}

		bulkImportSuccess.value = __("Imported {0} items", String(added));
		bulkImportRaw.value = "";
	} catch (e) {
		bulkImportError.value = String((e as Error)?.message || e);
	} finally {
		bulkImporting.value = false;
	}
};

const onImportFromSource = async (importedItems: any[]) => {
	let itemsToAdd = importedItems;
	if (serializationEnabled.value) {
		itemsToAdd = await serializationEngine.applySerialization(importedItems);
	}
	if (rfidEnabled.value && serializationEnabled.value) {
		itemsToAdd = itemsToAdd.map((item: any) => {
			const serial = item._generated_serials?.[0] || item.serial_no;
			if (serial) {
				const epcData = getEpcData(
					{ ...item, serial_no: serial },
					{ enabled: true, epcPrefix: rfidEpcPrefix.value },
				);
				return { ...item, _epc_data: epcData };
			}
			return item;
		});
	}
	importItems(itemsToAdd);
	useToastStore().show({
		title: __("Imported {0} items", [itemsToAdd.length]),
		color: "success",
	});
};

const thermalPrint = async () => {
	thermalPrinting.value = true;
	try {
		if (outputFormat.value === "zpl" || outputFormat.value === "epl") {
			await printLabelsRawWithFallback(items.value);
		} else {
			await printLabelsThermalWithFallback(items.value);
		}
	} finally {
		thermalPrinting.value = false;
	}
};

const onDesignerObjectChange = (id: string, updates: any) => {
	designer.updateObject(id, updates);
};

const onUploadImage = () => {
	const input = document.createElement("input");
	input.type = "file";
	input.accept = "image/*";
	input.onchange = (e: any) => {
		const file = e.target?.files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = (ev: any) => {
			const dataUrl = ev.target?.result;
			if (typeof dataUrl === "string") {
				const cx = designer.selectedObject.value
					? designer.selectedObject.value.x + 5
					: designer.labelSize.value.widthMm / 2 - 15;
				const cy = designer.selectedObject.value
					? designer.selectedObject.value.y + 5
					: designer.labelSize.value.heightMm / 2 - 7.5;
				designer.addImage(cx, cy, dataUrl, file.name);
				useToastStore().show({ title: __("Image added to canvas"), color: "success" });
			}
		};
		reader.readAsDataURL(file);
	};
	input.click();
};

const exportDesignerLayout = () => {
	const json = designer.exportLayout();
	const blob = new Blob([json], { type: "application/json" });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `label-layout-${pageFormat.value}.json`;
	a.click();
	URL.revokeObjectURL(url);
	useToastStore().show({ title: __("Layout exported"), color: "success" });
};

const importDesignerLayout = () => {
	const input = document.createElement("input");
	input.type = "file";
	input.accept = ".json";
	input.onchange = (e: any) => {
		const file = e.target?.files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = () => {
			try {
				designer.importLayout(String(reader.result));
				useToastStore().show({ title: __("Layout imported"), color: "success" });
			} catch (err) {
				useToastStore().show({ title: __("Invalid layout file"), color: "error" });
			}
		};
		reader.readAsText(file);
	};
	input.click();
};

const applyDesignerTemplate = () => {
	const json = designer.exportLayout();
	try {
		JSON.parse(json);
	} catch {
		useToastStore().show({ title: __("Invalid layout — cannot apply"), color: "error" });
		return;
	}
	setDesignerTemplate(json);
	useToastStore().show({ title: __("Designer template applied"), color: "success" });
	viewMode.value = "labels";
};

const saveTemplateDialog = ref(false);
const saveTemplateTitle = ref("");
const saveTemplateDescription = ref("");
const saveTemplateLoading = ref(false);

const onSaveTemplate = async () => {
	const title = saveTemplateTitle.value.trim();
	if (!title) {
		useToastStore().show({ title: __("Template title is required"), color: "error" });
		return;
	}
	const layoutJson = designer.exportLayout();
	try {
		JSON.parse(layoutJson);
	} catch {
		useToastStore().show({ title: __("Invalid layout — cannot save"), color: "error" });
		return;
	}
	saveTemplateLoading.value = true;
	try {
		await frappe.call({
			method: "posawesome.posawesome.api.label_templates.save_label_template",
			args: {
				title,
				label_size: pageFormat.value,
				layout_json: layoutJson,
				description: saveTemplateDescription.value.trim(),
			},
			silent: true,
		});
		useToastStore().show({ title: __("Template saved: {0}", [title]), color: "success" });
		saveTemplateDialog.value = false;
		saveTemplateTitle.value = "";
		saveTemplateDescription.value = "";
	} catch (e: any) {
		useToastStore().show({ title: __("Failed to save template"), color: "error" });
	} finally {
		saveTemplateLoading.value = false;
	}
};

const templateLibraryDialog = ref(false);
const verificationDialog = ref(false);

const loadTemplateFromLibrary = (tpl: any) => {
	if (tpl.layout_json) {
		try {
			designer.importLayout(tpl.layout_json);
			pageFormat.value = tpl.label_size;
			syncDesignerLabelSize();
		} catch (err) {
			useToastStore().show({ title: __("Failed to load template layout"), color: "error" });
		}
	}
};

const syncDesignerLabelSize = () => {
	const preset = PAGE_FORMAT_PRESETS.find((p) => p.value === pageFormat.value);
	if (preset && preset.widthMm && preset.heightMm) {
		const w = parseFloat(String(preset.widthMm));
		const h = parseFloat(String(preset.heightMm));
		if (w > 0 && h > 0) designer.setLabelSize(w, h);
	}
};

watch(viewMode, (mode) => {
	if (mode === "designer") {
		syncDesignerLabelSize();
	}
});

watch(pageFormat, () => {
	if (viewMode.value === "designer") {
		syncDesignerLabelSize();
	}
});

const sizeWarnings = computed(() => getLabelSizeWarnings());

const previewDialog = ref(false);
const previewContent = ref("");

const generateLabelsHtml = (items) => {
	const printable = getPrintableItems(items, { notify: false });
	if (!printable.length) return "";
	const style = printOutput.getPrintStyles();
	const content = printOutput.generatePrintContent(printable);
	return `<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<style>${style}</style>
	<style>
		@media screen {
			html,
			body {
				width: 100% !important;
				height: auto !important;
				min-height: 100% !important;
				overflow: auto !important;
				background: #eef2f7 !important;
			}
			body {
				box-sizing: border-box;
				margin: 0 !important;
				padding: 12px !important;
				display: flex;
				flex-wrap: wrap;
				align-items: flex-start;
				justify-content: center;
				gap: 12px;
			}
			.label-container {
				width: 100%;
				page-break-after: auto;
			}
			.label {
				flex: 0 0 auto;
				page-break-after: auto;
				background: #fff;
				box-shadow: 0 6px 18px rgba(15, 23, 42, 0.14);
			}
		}
		@media screen and (max-width: 600px) {
			body {
				padding: 8px !important;
				gap: 8px;
			}
		}
	</style>
</head>
<body>
	${content}
	<script src="/assets/posawesome/dist/js/libs/JsBarcode.all.min.js"><\/script>
	<script>
		try {
			JsBarcode(".barcode").init();
		} catch (error) {
			console.warn("Barcode preview could not render every barcode", error);
		}

		(function () {
			function fitLabels() {
				var maxWidth = Math.max(160, document.documentElement.clientWidth - 16);
				document.querySelectorAll(".label").forEach(function (label) {
					label.style.zoom = "1";
					var width = label.getBoundingClientRect().width;
					if (width > maxWidth) {
						label.style.zoom = (maxWidth / width).toFixed(3);
					}
				});
			}
			window.addEventListener("load", fitLabels);
			window.addEventListener("resize", fitLabels);
			if (document.readyState === "complete") {
				fitLabels();
			} else {
				setTimeout(fitLabels, 80);
			}
		})();
	<\/script>
</body>
</html>`;
};

const openPreview = () => {
	const html = generateLabelsHtml(items.value);
	if (!html) {
		useToastStore().show({ title: __("No items with barcodes to preview"), color: "warning" });
		return;
	}
	previewContent.value = html;
	previewDialog.value = true;
};

const printFromPreview = () => {
	if (previewContent.value) {
		printLabels(items.value);
		previewDialog.value = false;
	}
};

const pdfFromPreview = () => {
	if (previewContent.value) {
		downloadPdf(items.value);
		previewDialog.value = false;
	}
};

const onExportPng = () => {
	const printable = getPrintableItems(items.value, { notify: false });
	if (!printable.length) return;
	const style = printOutput.getPrintStyles();
	const content = printOutput.generatePrintContent(printable);
	exportPng(content, style);
};

const onExportSvg = () => {
	const printable = getPrintableItems(items.value, { notify: false });
	if (!printable.length) return;
	const style = printOutput.getPrintStyles();
	const content = printOutput.generatePrintContent(printable);
	exportSvg(content, style);
};

const onExportCsv = () => {
	const printable = getPrintableItems(items.value, { notify: false });
	if (!printable.length) return;
	exportCsv(printable);
};

const { shouldShowScaleGramsInput } = scaleSettings;

const headers = computed(() => [
	{ title: __("Item Code"), key: "item_code", width: "13%" },
	{ title: __("Item Name"), key: "item_name", width: "17%" },
	{ title: __("UOM"), key: "uom", width: "10%" },
	{ title: __("Price"), key: "price", width: "10%" },
	{ title: __("Barcode"), key: "barcode", width: "20%" },
	{ title: __("Weight (g)"), key: "grams", width: "10%" },
	{ title: __("Location"), key: "warehouseLocation", width: "10%" },
	{ title: __("Quantity"), key: "qty", align: "center" as const, width: "10%" },
	{ title: "", key: "variableData", align: "center" as const, sortable: false, width: "5%" },
	{ title: "", key: "actions", align: "center" as const, sortable: false, width: "5%" },
]);

watch(
	() => uiStore.posProfile,
	(profile) => {
		if (profile) {
			// POS profile is available for printOutput formatCurrency
		}
	},
	{ deep: true, immediate: true },
);

onMounted(() => {
	scaleSettings.ensureScaleBarcodeSettings();
});

onUnmounted(() => {
	cleanupQueue();
});
</script>

<style scoped>
.qty-control-btn {
	width: 24px !important;
	height: 24px !important;
	min-width: 24px !important;
	border-radius: 6px !important;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
	box-shadow:
		0 2px 8px var(--pos-shadow-light),
		0 1px 3px var(--pos-shadow-light) !important;
	font-weight: 600 !important;
	backdrop-filter: blur(10px) !important;
	position: relative !important;
	overflow: hidden !important;
	flex-shrink: 0;
}

.qty-control-btn::before {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: var(--pos-hover-bg);
	transition: transform 0.3s ease;
	transform: translateX(-100%);
	z-index: 0;
}

.qty-control-btn:hover::before {
	transform: translateX(0);
}

.qty-control-btn .v-icon {
	position: relative;
	z-index: 1;
}

.pos-table__qty-counter {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 2px;
	padding: 2px;
	min-width: 60px;
	max-width: 100px;
	width: auto;
	height: auto;
	background: var(--pos-surface-variant);
	border-radius: 8px;
	backdrop-filter: blur(10px);
	border: 1px solid var(--pos-border-light);
	transition: all 0.3s ease;
	margin: 0 auto;
	flex-shrink: 0;
	box-sizing: border-box;
}

.pos-table__qty-counter:hover {
	background: var(--pos-hover-bg);
	box-shadow: 0 4px 16px var(--pos-shadow);
	transform: translateY(-1px);
}

.pos-table__qty-display {
	min-width: 15px;
	max-width: 40px;
	width: auto;
	flex: 1 1 auto;
	text-align: center;
	font-weight: 600;
	padding: 0 2px;
	border-radius: 4px;
	background: var(--pos-primary-container);
	border: 1px solid var(--pos-primary-variant);
	font-family:
		"SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "Noto Sans Arabic", "Tahoma",
		sans-serif;
	font-variant-numeric: lining-nums tabular-nums;
	font-feature-settings:
		"tnum" 1,
		"lnum" 1,
		"kern" 1;
	color: var(--pos-primary);
	font-size: 0.75rem;
	transition: all 0.2s ease;
	box-shadow: 0 1px 3px var(--pos-shadow-light);
	display: flex;
	align-items: center;
	justify-content: center;
	height: 24px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	letter-spacing: -0.02em;
	word-spacing: -0.1em;
	cursor: pointer;
}

.pos-table__qty-display:focus-visible {
	outline: 2px solid var(--pos-primary);
	outline-offset: 2px;
	z-index: 10;
}

.qty-control-btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 2px 6px var(--pos-shadow) !important;
}

.qty-control-btn.minus-btn {
	background: var(--pos-button-warning-bg) !important;
	color: var(--pos-button-warning-text) !important;
	border: 2px solid var(--pos-button-warning-border) !important;
}

.qty-control-btn.minus-btn:hover {
	background: var(--pos-button-warning-hover-bg) !important;
	color: var(--pos-button-warning-hover-text) !important;
	box-shadow:
		0 6px 20px var(--pos-shadow),
		0 4px 8px var(--pos-shadow-light) !important;
	transform: translateY(-2px) scale(1.05) !important;
}

.qty-control-btn.plus-btn {
	background: var(--pos-button-success-bg) !important;
	color: var(--pos-button-success-text) !important;
	border: 2px solid var(--pos-button-success-border) !important;
}

.qty-control-btn.plus-btn:hover {
	background: var(--pos-button-success-hover-bg) !important;
	color: var(--pos-button-success-hover-text) !important;
	box-shadow:
		0 6px 20px var(--pos-shadow),
		0 4px 8px var(--pos-shadow-light) !important;
	transform: translateY(-2px) scale(1.05) !important;
}

.pos-table__qty-input {
	max-width: 80px;
	margin: 0 auto;
}
.pos-table__qty-input :deep(input) {
	text-align: center;
	font-weight: 600;
	-moz-appearance: textfield;
	appearance: textfield;
}
.pos-table__qty-input :deep(input::-webkit-outer-spin-button),
.pos-table__qty-input :deep(input::-webkit-inner-spin-button) {
	-webkit-appearance: none;
	appearance: none;
	margin: 0;
}
.pos-table__qty-input :deep(.v-input__control) {
	height: 24px;
}
.pos-table__qty-input :deep(.v-field__field) {
	height: 24px;
	padding: 0 4px;
}
.pos-table__qty-input :deep(.v-field__input) {
	padding: 0;
	min-height: 24px;
	font-size: 0.75rem;
}

/* ------------------------------------------------------------------ */
/* Handheld / narrow portrait layout (Sunmi V3, 6.75", 720x1600)       */
/* ------------------------------------------------------------------ */

@media (max-width: 959.98px) {
	.barcode-printing-page {
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
		overflow: hidden;
		background: rgb(var(--v-theme-background));
	}

	.barcode-mobile-header {
		display: flex;
		flex: 0 0 auto;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		padding: 8px 10px;
		border-bottom: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.28));
		background: var(--pos-surface, rgb(var(--v-theme-surface)));
		z-index: 2;
	}

	.barcode-mobile-header__copy {
		display: flex;
		flex-direction: column;
		min-width: 0;
		line-height: 1.2;
	}

	.barcode-mobile-header__title {
		font-size: 0.95rem;
		font-weight: 700;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.barcode-mobile-header__meta {
		font-size: 0.68rem;
		color: rgba(var(--v-theme-on-surface), 0.62);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.barcode-mobile-tabs {
		flex: 0 0 auto;
		max-width: 62%;
	}

	.barcode-mobile-tabs :deep(.v-btn) {
		min-width: 0;
		padding-inline: 8px;
		text-transform: none;
	}

	.barcode-mobile-tabs :deep(.v-btn__content) {
		font-size: 0.75rem;
		white-space: nowrap;
	}

	.barcode-mobile-tab-count {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 18px;
		height: 18px;
		margin-inline-start: 4px;
		padding-inline: 4px;
		border-radius: 999px;
		font-size: 0.65rem;
		font-weight: 700;
		line-height: 1;
		background: rgba(var(--v-theme-primary), 0.16);
		color: rgb(var(--v-theme-primary));
	}

	.barcode-printing-page > .v-row {
		flex: 1 1 auto;
		height: auto !important;
		min-height: 0;
		margin: 0 !important;
	}

	.barcode-pane-col {
		height: 100% !important;
		max-height: 100%;
		min-height: 0;
		padding: 0 !important;
		border: 0 !important;
	}

	.barcode-pane-hidden {
		display: none !important;
	}

	.barcode-pane-col--items {
		overflow-x: hidden;
		overflow-y: auto;
		-webkit-overflow-scrolling: touch;
	}

	.barcode-pane-col--workspace {
		overflow: hidden;
	}

	.barcode-pane-col--workspace > .v-card {
		height: 100% !important;
		min-height: 0;
		border-radius: 0;
	}

	.barcode-workspace-title {
		flex: 0 0 auto;
		min-height: 48px;
		gap: 6px;
		padding: 6px 8px !important;
	}

	.barcode-workspace-title__text {
		display: none;
	}

	.barcode-view-toggle {
		margin-inline-end: auto;
	}

	.barcode-view-toggle :deep(.v-btn) {
		min-width: 0;
		padding-inline: 10px;
	}

	.barcode-labels-body {
		padding: 10px !important;
	}

	.barcode-mobile-setup {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		margin-bottom: 10px;
		padding: 8px 10px;
		border: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.28));
		border-radius: 12px;
		background: var(--pos-surface-variant, rgba(148, 163, 184, 0.1));
	}

	.barcode-mobile-setup__copy {
		display: flex;
		flex-direction: column;
		gap: 4px;
		min-width: 0;
	}

	.barcode-mobile-setup__eyebrow {
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: rgba(var(--v-theme-on-surface), 0.62);
	}

	.barcode-mobile-setup__chips {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}

	.barcode-settings-block {
		margin-bottom: 8px;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.22));
	}

	.barcode-config-row,
	.barcode-option-row {
		row-gap: 2px;
	}

	.barcode-config-row :deep(.v-col),
	.barcode-option-row :deep(.v-col) {
		padding: 4px;
	}

	.barcode-option-row :deep(.v-checkbox .v-label) {
		font-size: 0.78rem;
		line-height: 1.15;
		white-space: normal;
	}

	.barcode-template-alert__body {
		flex-wrap: wrap;
		row-gap: 6px;
	}

	.barcode-template-alert__body :deep(.v-btn) {
		margin-inline-start: 0 !important;
	}

	.barcode-mobile-queue {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-top: 4px;
	}

	.barcode-mobile-queue__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}

	.barcode-mobile-queue__header > div {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}

	.barcode-mobile-queue__eyebrow {
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: rgba(var(--v-theme-on-surface), 0.62);
	}

	.barcode-mobile-queue__header strong {
		font-size: 0.9rem;
	}

	.barcode-mobile-queue__empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
		padding: 28px 16px;
		border: 1px dashed var(--pos-border-light, rgba(148, 163, 184, 0.4));
		border-radius: 14px;
		text-align: center;
		color: rgba(var(--v-theme-on-surface), 0.7);
	}

	.barcode-mobile-queue__empty strong {
		font-size: 0.95rem;
		color: rgb(var(--v-theme-on-surface));
	}

	.barcode-mobile-queue__empty span {
		max-width: 280px;
		font-size: 0.78rem;
		line-height: 1.35;
	}

	.barcode-mobile-queue__list {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 10px;
	}

	.barcode-queue-card {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-width: 0;
		padding: 10px;
		border: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.28));
		border-radius: 14px;
		background: var(--pos-surface, rgb(var(--v-theme-surface)));
	}

	.barcode-queue-card__head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 6px;
	}

	.barcode-queue-card__identity {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}

	.barcode-queue-card__identity strong {
		font-size: 0.86rem;
		line-height: 1.25;
		overflow-wrap: anywhere;
	}

	.barcode-queue-card__identity span {
		font-size: 0.68rem;
		color: rgba(var(--v-theme-on-surface), 0.6);
		overflow-wrap: anywhere;
	}

	.barcode-queue-card__barcode {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 6px;
		min-width: 0;
		padding: 6px 8px;
		border-radius: 9px;
		background: rgba(var(--v-theme-primary), 0.07);
	}

	.barcode-queue-card__barcode-value {
		flex: 1 1 120px;
		min-width: 0;
		font-family: ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace;
		font-size: 0.75rem;
		overflow-wrap: anywhere;
	}

	.barcode-queue-card__barcode-select {
		flex: 1 1 160px;
		min-width: 0;
	}

	.barcode-queue-card__fields {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 8px;
		align-items: end;
	}

	.barcode-queue-card__uom {
		min-width: 0;
	}

	.barcode-queue-card__metric {
		display: flex;
		flex-direction: column;
		gap: 3px;
		min-width: 0;
	}

	.barcode-queue-card__metric > span {
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: rgba(var(--v-theme-on-surface), 0.6);
	}

	.barcode-queue-card__metric > strong {
		font-size: 0.85rem;
		line-height: 1.2;
		white-space: nowrap;
		overflow-wrap: normal;
		word-break: normal;
	}

	.barcode-queue-card__metric:not(.barcode-queue-card__metric--qty) {
		grid-column: 1 / -1;
		padding: 4px 2px;
		border-bottom: 1px dashed var(--pos-border-light, rgba(148, 163, 184, 0.25));
	}

	.barcode-queue-card__metric--qty {
		grid-column: span 1;
	}

	.barcode-queue-card__metric--qty .pos-table__qty-counter {
		width: 100%;
		max-width: 150px;
	}

	.barcode-queue-card__weight,
	.barcode-queue-card__location {
		grid-column: 1 / -1;
		min-width: 0;
	}

	.barcode-queue-card__footer {
		display: flex;
		justify-content: flex-end;
		border-top: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.2));
		padding-top: 2px;
	}

	.barcode-mobile-items-bar {
		display: flex;
		flex: 0 0 auto;
		padding: 8px 10px calc(8px + env(safe-area-inset-bottom, 0px));
		border-top: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.3));
		background: var(--pos-surface, rgb(var(--v-theme-surface)));
	}

	.barcode-mobile-items-bar :deep(.v-btn) {
		text-transform: none;
	}

	.barcode-mobile-items-bar__count {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 22px;
		height: 22px;
		margin-inline-start: 8px;
		padding-inline: 6px;
		border-radius: 999px;
		font-size: 0.72rem;
		font-weight: 700;
		line-height: 1;
		background: rgba(255, 255, 255, 0.24);
	}

	.barcode-mobile-printbar {
		display: grid;
		flex: 0 0 auto;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 4px;
		padding: 6px 8px calc(6px + env(safe-area-inset-bottom, 0px));
		border-top: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.3));
		background: var(--pos-surface, rgb(var(--v-theme-surface)));
	}

	.barcode-mobile-printbar :deep(.v-btn) {
		min-width: 0;
		height: 52px;
		padding: 0 2px;
		text-transform: none;
	}

	.barcode-mobile-printbar :deep(.v-btn__content) {
		display: flex;
		flex-direction: column;
		gap: 2px;
		font-size: 0.68rem;
		line-height: 1.1;
		white-space: nowrap;
	}

	.barcode-designer-body {
		flex-direction: column !important;
		min-height: 0;
		overflow-y: auto;
		-webkit-overflow-scrolling: touch;
	}

	.barcode-designer-canvas {
		flex: 0 0 auto !important;
		height: 46vh;
		min-height: 300px;
	}

	.barcode-designer-panel {
		width: 100% !important;
		max-height: 45vh;
		overflow-y: auto;
		border-top: 1px solid var(--pos-border-light, rgba(148, 163, 184, 0.3));
	}

	.barcode-designer-panel :deep(.panel-root) {
		height: auto !important;
	}

	.barcode-designer-actions {
		flex-direction: column !important;
		align-items: stretch !important;
	}

	.barcode-designer-actions__group {
		flex-wrap: wrap;
	}

	.barcode-designer-actions__group :deep(.v-btn) {
		flex: 1 1 45%;
		min-width: 0;
		text-transform: none;
	}

	.barcode-preview-card {
		height: 100dvh;
		max-height: 100dvh;
		min-height: 0;
	}

	.barcode-preview-frame {
		flex: 1 1 auto;
		min-height: 0;
		background: #eef2f7;
	}

	.barcode-preview-actions {
		flex: 0 0 auto;
		flex-wrap: wrap;
		gap: 8px;
		padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px)) !important;
	}

	.barcode-dialog-actions {
		flex-wrap: wrap;
		gap: 8px;
	}

	.barcode-dialog-actions__start,
	.barcode-dialog-actions__end {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.barcode-dialog-actions__end {
		margin-inline-start: auto;
	}
}

@media (max-width: 600px) {
	.barcode-mobile-header__meta {
		display: none;
	}

	.barcode-preview-actions :deep(.v-btn) {
		flex: 1 1 40%;
		margin: 0 !important;
	}

	.barcode-preview-actions :deep(.v-btn:last-child) {
		flex-basis: 100%;
	}
}
</style>
