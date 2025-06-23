<template>
  <v-container class="app-container" fluid>
    <!-- 加载状态 -->
    <v-row v-if="loading" justify="center">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          size="64"
          color="primary"
        ></v-progress-circular>
        <v-card-text class="mt-4 text-h6 pa-0">加载项目详情中...</v-card-text>
      </v-col>
    </v-row>

    <!-- 错误状态 -->
    <v-row v-else-if="error" justify="center">
      <v-col cols="12" md="8">
        <v-alert type="error" prominent>
          <v-alert-title>加载失败</v-alert-title>
          {{ error }}
        </v-alert>
        <v-sheet class="text-center mt-4" color="transparent">
          <v-btn color="primary" @click="loadProjectDetail" class="app-button"
            >重试</v-btn
          >
          <v-btn
            color="secondary"
            @click="$router.go(-1)"
            class="ml-2 app-button"
            >返回</v-btn
          >
        </v-sheet>
      </v-col>
    </v-row>

    <!-- 项目详情内容 -->
    <v-container v-else-if="project" fluid>
      <!-- 页面标题和操作按钮 - 统一设计 -->
      <v-sheet class="app-section" color="transparent">
        <v-sheet class="d-flex align-center justify-space-between flex-wrap ga-4" color="transparent">
          <v-sheet class="d-flex align-center" color="transparent">
            <v-btn icon @click="$router.go(-1)" class="mr-3 app-button">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <v-sheet color="transparent">
              <h1 class="text-h4 font-weight-medium mb-2">
                {{ project.project_name }}
              </h1>
              <v-sheet class="d-flex ga-2" color="transparent">
                <v-chip color="primary" class="app-chip">{{
                  project.category
                }}</v-chip>
                <v-chip
                  :color="getStatusColor(project.project_status)"
                  class="app-chip"
                >
                  {{ project.project_status || "进行中" }}
                </v-chip>
              </v-sheet>
            </v-sheet>
          </v-sheet>
          <v-sheet class="d-flex ga-2" color="transparent">
            <v-btn
              :color="isWatched ? 'error' : 'warning'"
              :prepend-icon="isWatched ? 'mdi-heart' : 'mdi-heart-outline'"
              @click="toggleWatch"
              :loading="watchLoading"
              class="app-button"
            >
              {{ isWatched ? "取消关注" : "添加关注" }}
            </v-btn>
            <v-btn
              color="primary"
              :href="project.project_url"
              target="_blank"
              prepend-icon="mdi-open-in-new"
              class="app-button"
            >
              访问原始项目
            </v-btn>
            <v-btn
              color="secondary"
              @click="exportProjectData"
              prepend-icon="mdi-download"
              :loading="exporting"
              class="app-button"
            >
              导出数据
            </v-btn>
          </v-sheet>
        </v-sheet>
      </v-sheet>

      <!-- 项目基本信息卡片 - 统一设计 -->
      <v-row class="app-section">
        <v-col cols="12" md="4">
          <v-card class="h-100 app-card">
            <v-img
              :src="
                isValidImageUrl(project.project_image)
                  ? project.project_image
                  : '/placeholder-image.jpg'
              "
              height="200"
              cover
              class="white--text"
            >
              <template v-slot:placeholder>
                <v-row class="fill-height ma-0" align="center" justify="center">
                  <v-progress-circular
                    indeterminate
                    color="on-surface-variant"
                  ></v-progress-circular>
                </v-row>
              </template>
              <template v-slot:error>
                <v-row class="fill-height ma-0" align="center" justify="center">
                  <v-icon size="64" color="on-surface-variant"
                    >mdi-image-off</v-icon
                  >
                </v-row>
              </template>
            </v-img>
            <v-card-text>
              <v-card-text class="text-h6 mb-2 pa-0">作者信息</v-card-text>
              <v-sheet class="d-flex align-center mb-2" color="transparent">
                <v-avatar size="32" class="mr-2">
                  <v-img
                    v-if="isValidImageUrl(project.author_image)"
                    :src="project.author_image"
                  >
                    <template v-slot:error>
                      <v-icon icon="mdi-account" size="20" />
                    </template>
                  </v-img>
                  <v-icon v-else icon="mdi-account" size="20" />
                </v-avatar>
                <v-sheet color="transparent">
                  <v-card-text class="font-weight-medium pa-0">
                    {{ project.author_name || "未知作者" }}
                  </v-card-text>
                  <a
                    v-if="project.author_link"
                    :href="project.author_link"
                    target="_blank"
                    class="text-caption text-primary"
                  >
                    查看作者主页
                  </a>
                </v-sheet>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="h-100 app-card">
            <v-card-title class="p-lg">
              <v-avatar color="primary" size="32" class="me-3">
                <v-icon icon="mdi-chart-bar" color="on-primary" size="18" />
              </v-avatar>
              <v-sheet color="transparent">
                <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                  项目数据
                </v-card-text>
                <v-card-text class="text-body-2 text-on-surface-variant pa-0">
                  筹款进度和支持情况
                </v-card-text>
              </v-sheet>
            </v-card-title>
            <v-card-text class="p-lg pt-0">
              <v-row>
                <v-col cols="6" md="3">
                  <v-sheet class="text-center" color="transparent">
                    <v-card-text class="text-h4 font-weight-bold text-primary pa-0">
                      ¥{{ formatNumber(project.raised_amount) }}
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      已筹金额
                    </v-card-text>
                  </v-sheet>
                </v-col>
                <v-col cols="6" md="3">
                  <v-sheet class="text-center" color="transparent">
                    <v-card-text class="text-h4 font-weight-bold text-on-surface pa-0">
                      ¥{{ formatNumber(project.target_amount) }}
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      目标金额
                    </v-card-text>
                  </v-sheet>
                </v-col>
                <v-col cols="6" md="3">
                  <v-sheet class="text-center" color="transparent">
                    <v-card-text class="text-h4 font-weight-bold text-success pa-0">
                      {{ project.completion_rate?.toFixed(1) || 0 }}%
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      完成率
                    </v-card-text>
                  </v-sheet>
                </v-col>
                <v-col cols="6" md="3">
                  <v-sheet class="text-center" color="transparent">
                    <v-card-text class="text-h4 font-weight-bold text-on-surface pa-0">
                      {{ project.backer_count || 0 }}
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      支持者
                    </v-card-text>
                  </v-sheet>
                </v-col>
              </v-row>

              <v-progress-linear
                :model-value="project.completion_rate || 0"
                height="8"
                color="primary"
                class="my-4"
              ></v-progress-linear>

              <v-row>
                <v-col cols="4">
                  <v-sheet class="text-center" color="transparent">
                    <v-icon color="error" class="mb-1">mdi-heart</v-icon>
                    <v-card-text class="font-weight-medium text-on-surface pa-0">
                      {{ project.supporter_count || 0 }}
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      点赞数
                    </v-card-text>
                  </v-sheet>
                </v-col>
                <v-col cols="4">
                  <v-sheet class="text-center" color="transparent">
                    <v-icon color="info" class="mb-1">mdi-comment</v-icon>
                    <v-card-text class="font-weight-medium text-on-surface pa-0">
                      {{ project.comment_count || 0 }}
                    </v-card-text>
                    <v-card-text class="text-caption text-on-surface-variant pa-0">
                      评论数
                    </v-card-text>
                  </v-sheet>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 项目时间信息 - 统一设计 -->
      <v-row class="app-section">
        <v-col cols="12">
          <v-card class="app-card">
            <v-card-title class="p-lg">
              <v-avatar color="info" size="32" class="me-3">
                <v-icon icon="mdi-clock-outline" color="on-info" size="18" />
              </v-avatar>
              <v-sheet color="transparent">
                <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                  时间信息
                </v-card-text>
                <v-card-text class="text-body-2 text-on-surface-variant pa-0">
                  项目时间线和爬取记录
                </v-card-text>
              </v-sheet>
            </v-card-title>
            <v-card-text class="p-lg pt-0">
              <v-row>
                <v-col cols="12" md="3">
                  <v-card-text class="text-subtitle-2 mb-1 text-on-surface-variant pa-0">
                    开始时间
                  </v-card-text>
                  <v-card-text class="text-on-surface pa-0">
                    {{ formatDate(project.start_time) }}
                  </v-card-text>
                </v-col>
                <v-col cols="12" md="3">
                  <v-card-text class="text-subtitle-2 mb-1 text-on-surface-variant pa-0">
                    结束时间
                  </v-card-text>
                  <v-card-text class="text-on-surface pa-0">
                    {{ formatDate(project.end_time) }}
                  </v-card-text>
                </v-col>
                <v-col cols="12" md="3">
                  <v-card-text class="text-subtitle-2 mb-1 text-on-surface-variant pa-0">
                    最后爬取
                  </v-card-text>
                  <v-card-text class="text-on-surface pa-0">
                    {{ formatDate(project.crawl_time) }}
                  </v-card-text>
                </v-col>
                <v-col cols="12" md="3">
                  <v-card-text class="text-subtitle-2 mb-1 text-on-surface-variant pa-0">
                    项目ID
                  </v-card-text>
                  <v-card-text class="font-family-monospace text-on-surface pa-0">
                    {{ project.project_id }}
                  </v-card-text>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 回报列表 - 统一设计 -->
      <v-row v-if="rewards && rewards.length > 0" class="app-section">
        <v-col cols="12">
          <v-card class="app-card">
            <v-card-title class="p-lg">
              <v-avatar color="warning" size="32" class="me-3">
                <v-icon icon="mdi-gift" color="on-warning" size="18" />
              </v-avatar>
              <v-sheet class="flex-grow-1" color="transparent">
                <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                  回报列表
                </v-card-text>
                <v-card-text class="text-body-2 text-on-surface-variant pa-0">
                  项目支持档位详情
                </v-card-text>
              </v-sheet>
              <v-chip color="primary" class="app-chip"
                >{{ rewards.length }}个档位</v-chip
              >
            </v-card-title>
            <v-card-text class="p-lg pt-0">
              <v-row>
                <v-col
                  v-for="(reward, index) in rewards"
                  :key="index"
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-card variant="outlined" class="h-100 app-card">
                    <v-card-title
                      class="d-flex justify-space-between align-center"
                    >
                      <v-card-text class="pa-0">¥{{ formatNumber(reward.price || 0) }}</v-card-text>
                      <v-chip
                        size="small"
                        :color="reward.is_sold_out ? 'error' : 'success'"
                        variant="tonal"
                        class="app-chip"
                      >
                        {{ reward.is_sold_out ? "已售罄" : "可支持" }}
                      </v-chip>
                    </v-card-title>
                    <v-card-text>
                      <v-card-text class="font-weight-medium mb-2 text-on-surface pa-0">
                        {{ reward.title || "未命名档位" }}
                      </v-card-text>
                      <v-card-text class="text-caption mb-2 text-on-surface-variant pa-0">
                        {{ reward.content || "无详细描述" }}
                      </v-card-text>
                      <v-sheet class="d-flex justify-space-between text-caption" color="transparent">
                        <v-chip class="text-on-surface-variant" variant="text" size="small">
                          <v-icon size="small" color="primary"
                            >mdi-account-multiple</v-icon
                          >
                          {{ reward.backer_count || 0 }}人支持
                        </v-chip>
                        <v-chip
                          v-if="reward.is_limited"
                          class="text-on-surface-variant"
                          variant="text"
                          size="small"
                        >
                          <v-icon size="small" color="warning"
                            >mdi-timer-sand</v-icon
                          >
                          剩余{{ reward.remaining_count || 0 }}个
                        </v-chip>
                      </v-sheet>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 历史数据追踪 -->
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary"
                >mdi-chart-timeline-variant</v-icon
              >
              <v-chip class="text-on-surface" variant="text">历史数据追踪</v-chip>
              <v-spacer></v-spacer>
              <v-btn
                size="small"
                @click="loadProjectHistory"
                :loading="historyLoading"
                prepend-icon="mdi-refresh"
                variant="tonal"
                color="primary"
              >
                刷新
              </v-btn>
            </v-card-title>
            <v-card-text>
              <!-- 统计信息 -->
              <v-sheet v-if="statistics && statistics.trends" class="mb-4" color="transparent">
                <v-row>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text
                        class="text-h6 font-weight-bold pa-0"
                        :class="
                          getTrendColorClass(
                            statistics.trends.raised_amount?.change_rate,
                          )
                        "
                      >
                        {{
                          formatGrowth(
                            statistics.trends.raised_amount?.change_rate,
                          )
                        }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        资金增长率
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant mt-1 pa-0">
                        {{
                          formatChange(
                            statistics.trends.raised_amount?.change,
                            "¥",
                          )
                        }}
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text
                        class="text-h6 font-weight-bold pa-0"
                        :class="
                          getTrendColorClass(
                            statistics.trends.backer_count?.change_rate,
                          )
                        "
                      >
                        {{
                          formatGrowth(
                            statistics.trends.backer_count?.change_rate,
                          )
                        }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        支持者增长率
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant mt-1 pa-0">
                        {{
                          formatChange(
                            statistics.trends.backer_count?.change,
                            "",
                          )
                        }}
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text
                        class="text-h6 font-weight-bold pa-0"
                        :class="
                          getTrendColorClass(
                            statistics.trends.like_count?.change_rate,
                          )
                        "
                      >
                        {{
                          formatGrowth(
                            statistics.trends.like_count?.change_rate,
                          )
                        }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        点赞增长率
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant mt-1 pa-0">
                        {{
                          formatChange(statistics.trends.like_count?.change, "")
                        }}
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text
                        class="text-h6 font-weight-bold pa-0"
                        :class="
                          getTrendColorClass(
                            statistics.trends.comment_count?.change_rate,
                          )
                        "
                      >
                        {{
                          formatGrowth(
                            statistics.trends.comment_count?.change_rate,
                          )
                        }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        评论增长率
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant mt-1 pa-0">
                        {{
                          formatChange(
                            statistics.trends.comment_count?.change,
                            "",
                          )
                        }}
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>

                <!-- 历史数据概览 -->
                <v-row class="mt-2">
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                        {{ statistics.total_records || 0 }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        历史记录数
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                        {{ formatRelativeTime(statistics.first_crawl) }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        首次爬取
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text class="text-h6 font-weight-bold text-on-surface pa-0">
                        {{ formatRelativeTime(statistics.last_crawl) }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        最近爬取
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <v-card-text
                        class="text-h6 font-weight-bold pa-0"
                        :class="
                          statistics.has_changes
                            ? 'text-success'
                            : 'text-on-surface-variant'
                        "
                      >
                        {{ statistics.has_changes ? "有变化" : "无变化" }}
                      </v-card-text>
                      <v-card-text class="text-caption text-on-surface-variant pa-0">
                        数据状态
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-sheet>

              <!-- 增长率分析面板 -->
              <v-sheet v-if="history.length >= 2" class="mb-6" color="transparent">
                <GrowthAnalysisPanel :history-data="history" />
              </v-sheet>

              <!-- 历史数据趋势图表 -->
              <v-sheet v-if="history.length >= 2" class="mb-6" color="transparent">
                <HistoryTrendChart :history-data="history" :height="400" />
              </v-sheet>

              <!-- 历史记录时间线 -->
              <v-sheet v-if="history.length > 0" color="transparent">
                <v-sheet class="d-flex align-center mb-4" color="transparent">
                  <v-icon class="mr-2" color="primary"
                    >mdi-timeline-clock</v-icon
                  >
                  <v-chip class="text-h6 font-weight-bold text-on-surface" variant="text"
                    >详细时间线</v-chip
                  >
                  <v-spacer></v-spacer>
                  <v-chip color="info" size="small" variant="outlined">
                    {{ history.length }} 条记录
                  </v-chip>
                </v-sheet>
                <v-timeline density="compact">
                  <v-timeline-item
                    v-for="(record, index) in displayedTimelineHistory"
                    :key="index"
                    :dot-color="index === 0 ? 'primary' : 'on-surface-variant'"
                    size="small"
                  >
                    <template v-slot:opposite>
                      <v-sheet class="text-caption text-on-surface-variant" color="transparent">
                        <v-card-text class="pa-0">{{ formatDate(record.crawl_time) }}</v-card-text>
                        <v-card-text class="text-caption text-on-surface-variant mt-1 pa-0">
                          {{ formatRelativeTime(record.crawl_time) }}
                        </v-card-text>
                      </v-sheet>
                    </template>

                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="py-2">
                        <v-sheet class="d-flex justify-space-between align-center" color="transparent">
                          <v-sheet color="transparent">
                            <v-card-text class="font-weight-medium text-on-surface pa-0">
                              ¥{{ formatNumber(record.raised_amount) }}
                              <v-chip
                                class="text-caption text-on-surface-variant"
                                variant="text"
                                size="x-small"
                              >
                                ({{ record.completion_rate?.toFixed(1) || 0 }}%)
                              </v-chip>
                            </v-card-text>
                            <v-card-text class="text-caption text-on-surface-variant pa-0">
                              支持者: {{ record.backer_count || 0 }} | 点赞:
                              {{ record.supporter_count || 0 }} | 评论:
                              {{ record.comment_count || 0 }}
                            </v-card-text>
                          </v-sheet>
                          <v-sheet
                            v-if="index < displayedTimelineHistory.length - 1"
                            class="text-right"
                            color="transparent"
                          >
                            <v-chip
                              class="text-caption"
                              :class="
                                getChangeColorClass(
                                  record.raised_amount -
                                    displayedTimelineHistory[index + 1]
                                      .raised_amount,
                                )
                              "
                              variant="text"
                              size="x-small"
                            >
                              {{
                                formatChange(
                                  record.raised_amount -
                                    displayedTimelineHistory[index + 1]
                                      .raised_amount,
                                  "¥",
                                )
                              }}
                            </v-chip>
                          </v-sheet>
                        </v-sheet>
                      </v-card-text>
                    </v-card>
                  </v-timeline-item>
                </v-timeline>

                <!-- 展开更多时间线记录 -->
                <v-sheet v-if="hasMoreTimelineRecords" class="text-center mt-4" color="transparent">
                  <v-btn
                    @click="expandTimeline"
                    variant="outlined"
                    color="primary"
                  >
                    展开更多时间线记录 ({{
                      history.length - timelineDisplayLimit
                    }}
                    条)
                  </v-btn>
                </v-sheet>

                <!-- 加载更多历史数据 -->
                <v-sheet
                  v-if="history.length < totalHistoryCount"
                  class="text-center mt-4"
                  color="transparent"
                >
                  <v-btn
                    @click="loadMoreHistory"
                    :loading="historyLoading"
                    variant="outlined"
                    color="secondary"
                  >
                    加载更多历史记录
                  </v-btn>
                </v-sheet>
              </v-sheet>

              <!-- 无历史数据 -->
              <v-sheet v-else-if="!historyLoading" class="text-center py-8" color="transparent">
                <v-icon size="64" color="on-surface-variant"
                  >mdi-history</v-icon
                >
                <v-card-text class="text-h6 mt-2 text-on-surface pa-0">暂无历史数据</v-card-text>
                <v-card-text class="text-caption text-on-surface-variant pa-0">
                  该项目还没有历史爬取记录
                </v-card-text>
              </v-sheet>

              <!-- 历史数据加载状态 -->
              <v-sheet v-if="historyLoading" class="text-center py-4" color="transparent">
                <v-progress-circular
                  indeterminate
                  size="32"
                  color="primary"
                ></v-progress-circular>
                <v-card-text class="mt-2 text-on-surface-variant pa-0">
                  加载历史数据中...
                </v-card-text>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useSnackbar } from "@/composables/useSnackbar";
import axios from "axios";
import { isValidImageUrl } from "@/utils/imageUtils";
import { formatDateTime, formatRelativeTime } from "@/utils/timeUtils";
import GrowthAnalysisPanel from "@/components/GrowthAnalysisPanel.vue";
import HistoryTrendChart from "@/components/HistoryTrendChart.vue";

const route = useRoute();
const { showSnackbar } = useSnackbar();

// 响应式数据
const loading = ref(true);
const historyLoading = ref(false);
const exporting = ref(false);
const watchLoading = ref(false);
const error = ref("");
const project = ref(null);
const statistics = ref(null);
const history = ref([]);
const rewards = ref([]);
const totalHistoryCount = ref(0);
const historyOffset = ref(0);
const historyLimit = ref(10);
const timelineDisplayLimit = ref(5); // 时间线显示限制
const isWatched = ref(false);

// 计算属性
const projectId = computed(() => route.params.id);

// 时间线显示的历史记录（限制数量避免过长）
const displayedTimelineHistory = computed(() => {
  return history.value.slice(0, timelineDisplayLimit.value);
});

// 是否有更多时间线记录
const hasMoreTimelineRecords = computed(() => {
  return history.value.length > timelineDisplayLimit.value;
});

// 生命周期
onMounted(() => {
  loadProjectDetail();
  checkWatchStatus();
});

// 方法
async function loadProjectDetail() {
  try {
    loading.value = true;
    error.value = "";

    const response = await axios.get(`/api/projects/${projectId.value}/detail`);

    if (response.data.success) {
      project.value = response.data.project;
      statistics.value = response.data.statistics;

      // 解析回报数据
      parseRewardsData(response.data.project.rewards_data);

      // 加载历史数据
      await loadProjectHistory();
    } else {
      error.value = response.data.message || "加载项目详情失败";
    }
  } catch (err) {
    console.error("加载项目详情失败:", err);
    error.value = err.response?.data?.message || "网络错误，请稍后重试";
  } finally {
    loading.value = false;
  }
}

async function loadProjectHistory() {
  try {
    historyLoading.value = true;

    const response = await axios.get(
      `/api/projects/${projectId.value}/history`,
      {
        params: {
          limit: historyLimit.value,
          offset: historyOffset.value,
        },
      },
    );

    if (response.data.success) {
      if (historyOffset.value === 0) {
        history.value = response.data.history;
      } else {
        history.value.push(...response.data.history);
      }
      totalHistoryCount.value = response.data.total_count;
    } else {
      showSnackbar(response.data.message || "加载历史数据失败", "error");
    }
  } catch (err) {
    console.error("加载历史数据失败:", err);
    showSnackbar("加载历史数据失败", "error");
  } finally {
    historyLoading.value = false;
  }
}

async function loadMoreHistory() {
  historyOffset.value += historyLimit.value;
  await loadProjectHistory();
}

function expandTimeline() {
  timelineDisplayLimit.value = Math.min(
    timelineDisplayLimit.value + 10,
    history.value.length,
  );
}

async function exportProjectData() {
  try {
    exporting.value = true;

    const response = await axios.get(
      `/api/projects/${projectId.value}/export`,
      {
        responseType: "blob",
      },
    );

    // 创建下载链接
    const blob = new Blob([response.data], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `project_${projectId.value}_history.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    showSnackbar("数据导出成功", "success");
  } catch (err) {
    console.error("导出数据失败:", err);
    showSnackbar("导出数据失败", "error");
  } finally {
    exporting.value = false;
  }
}

function parseRewardsData(rewardsDataStr) {
  try {
    rewards.value = [];

    if (
      !rewardsDataStr ||
      rewardsDataStr === "none" ||
      rewardsDataStr === "[]" ||
      rewardsDataStr === ""
    ) {
      return;
    }

    // 根据爬虫代码分析，rewards_data实际存储的是回报数量，不是具体的回报数据
    // 爬虫存储格式：[str(rewards_list), len(rewards_list)]
    // 其中rewards_list包含的是字符串化的回报数据

    // 如果只是数字，说明这是回报数量，而不是具体的回报数据
    if (/^\d+$/.test(rewardsDataStr.toString().trim())) {
      const rewardCount = parseInt(rewardsDataStr);
      if (rewardCount > 0) {
        // 创建占位符回报数据
        rewards.value = Array.from(
          { length: Math.min(rewardCount, 10) },
          (_, index) => ({
            id: index,
            price: 0,
            backer_count: 0,
            title: `回报档位 ${index + 1}`,
            content: "回报详情需要重新爬取获取",
            time_info: "",
            is_limited: false,
            remaining_count: 0,
            is_sold_out: false,
          }),
        );
        console.log(`发现 ${rewardCount} 个回报档位，但详细数据需要重新爬取`);
        return;
      }
    }

    // 尝试解析复杂的回报数据格式
    let rewardsData;

    if (typeof rewardsDataStr === "string") {
      // 处理字符串化的数组格式
      if (rewardsDataStr.startsWith("[") && rewardsDataStr.endsWith("]")) {
        try {
          rewardsData = JSON.parse(rewardsDataStr);
        } catch {
          // 如果JSON解析失败，尝试其他方式
          const matches = rewardsDataStr.match(/\[([^\]]+)\]/g);
          if (matches) {
            rewardsData = matches.map((match) => {
              try {
                return JSON.parse(match);
              } catch {
                return match
                  .slice(1, -1)
                  .split(",")
                  .map((s) => s.trim().replace(/['"]/g, ""));
              }
            });
          }
        }
      }
    } else if (Array.isArray(rewardsDataStr)) {
      rewardsData = rewardsDataStr;
    }

    if (rewardsData && Array.isArray(rewardsData)) {
      rewards.value = rewardsData
        .map((reward, index) => {
          if (Array.isArray(reward) && reward.length >= 6) {
            // 处理爬虫格式：[title, sign_logo, back_money, backers, time_info, detail]
            const [title, sign_logo, back_money, backers, time_info, detail] =
              reward;
            return {
              id: index,
              title: title !== "none" ? title : `回报档位 ${index + 1}`,
              price: parseFloat(back_money) || 0,
              backer_count:
                backers === "已满" ? "已满" : parseInt(backers) || 0,
              content: detail !== "none" ? detail : "无详细描述",
              time_info: time_info !== "none" ? time_info : "",
              is_limited: sign_logo.includes("限量"),
              remaining_count: 0,
              is_sold_out: backers === "已满",
            };
          } else if (typeof reward === "object") {
            // 处理对象格式的回报数据
            return {
              id: reward.id || index,
              price: parseFloat(reward.price || reward.money || 0),
              backer_count: parseInt(
                reward.backer_count || reward.back_count || 0,
              ),
              title: reward.title || reward.name || `回报档位 ${index + 1}`,
              content: reward.content || reward.description || "无详细描述",
              is_limited: reward.max_total > 0,
              remaining_count: Math.max(
                0,
                (reward.max_total || 0) - (reward.backer_count || 0),
              ),
              is_sold_out:
                reward.status === "sold_out" ||
                reward.backer_count >= reward.max_total,
            };
          }
          return null;
        })
        .filter(Boolean);
    }

    console.log("解析回报数据:", rewards.value);
  } catch (error) {
    console.warn("解析回报数据失败:", error, rewardsDataStr);
    rewards.value = [];
  }
}

// 工具函数
function formatNumber(num) {
  if (!num) return "0";
  return new Intl.NumberFormat("zh-CN").format(num);
}

function formatDate(dateStr) {
  if (!dateStr) return "未知";
  try {
    // 使用统一的时间工具，显示访问者本地时区
    return formatDateTime(dateStr, "YYYY-MM-DD HH:mm:ss");
  } catch {
    return dateStr;
  }
}

function formatGrowth(growth) {
  if (growth === undefined || growth === null) return "0%";
  const sign = growth >= 0 ? "+" : "";
  return `${sign}${growth.toFixed(1)}%`;
}

function formatChange(value, prefix = "") {
  if (value === undefined || value === null || isNaN(value)) return "无变化";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${prefix}${Math.abs(value).toLocaleString()}`;
}

// MD3标准颜色CSS类函数
function getTrendColorClass(value) {
  if (value > 0) return "text-success";
  if (value < 0) return "text-error";
  return "text-on-surface-variant";
}

function getChangeColorClass(value) {
  if (value > 0) return "text-success";
  if (value < 0) return "text-error";
  return "text-on-surface-variant";
}

// 旧函数已移除，现在使用MD3标准的颜色样式函数

function getStatusColor(status) {
  switch (status) {
    case "成功":
      return "success";
    case "失败":
      return "error";
    case "进行中":
      return "primary";
    default:
      return "grey";
  }
}

// 关注功能相关方法
async function checkWatchStatus() {
  try {
    const response = await axios.get(`/api/watch/check/${projectId.value}`);
    if (response.data.success) {
      isWatched.value = response.data.is_watched;
    }
  } catch (error) {
    console.error("检查关注状态失败:", error);
  }
}

async function toggleWatch() {
  try {
    watchLoading.value = true;

    if (isWatched.value) {
      // 取消关注
      const response = await axios.post("/api/watch/remove", {
        project_id: projectId.value,
      });

      if (response.data.success) {
        isWatched.value = false;
        showSnackbar("已取消关注", "success");
      } else {
        showSnackbar(response.data.message || "取消关注失败", "error");
      }
    } else {
      // 添加关注
      const response = await axios.post("/api/watch/add", {
        project_id: projectId.value,
        project_name: project.value?.project_name || "",
        project_url: project.value?.project_url || "",
        category: project.value?.category || "",
        author_name: project.value?.author_name || "",
      });

      if (response.data.success) {
        isWatched.value = true;
        showSnackbar("已添加到关注列表", "success");
      } else {
        showSnackbar(response.data.message || "添加关注失败", "error");
      }
    }
  } catch (error) {
    console.error("切换关注状态失败:", error);
    showSnackbar("操作失败，请稍后重试", "error");
  } finally {
    watchLoading.value = false;
  }
}
</script>

<style scoped>
/* ProjectDetail 统一设计样式 */
.font-family-monospace {
  font-family: "Courier New", monospace;
}

.v-timeline-item {
  padding-bottom: var(--spacing-sm);
}

/* 样式现在完全由Vuetify defaults配置管理 */

/* MD3 统计卡片样式 */
.v-card[variant="outlined"] {
  transition: background-color var(--md3-motion-duration-short)
    var(--md3-motion-easing-standard);

  &:hover {
    background-color: rgba(
      var(--v-theme-primary),
      var(--md3-state-hover-opacity)
    );
  }
}

/* MD3 时间线卡片样式 - 通过Vuetify配置管理颜色 */
.v-timeline .v-card {
  transition: background-color var(--md3-motion-duration-short)
    var(--md3-motion-easing-standard);

  &:hover {
    background-color: rgba(
      var(--v-theme-primary),
      var(--md3-state-hover-opacity)
    );
  }
}

/* MD3 回报卡片样式 */
.reward-card {
  transition: background-color var(--md3-motion-duration-short)
    var(--md3-motion-easing-standard);

  &:hover {
    background-color: rgba(
      var(--v-theme-primary),
      var(--md3-state-hover-opacity)
    );
  }
}

/* 头像样式 */
.v-avatar {
  transition: var(--transition-fast);
}

/* 响应式优化 */
@media (max-width: 599px) {
  .d-flex.justify-space-between {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .text-right {
    text-align: left;
  }
}
</style>
