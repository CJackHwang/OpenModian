<template>
  <div>
    <!-- 备份操作面板 - 统一设计 -->
    <v-card class="mb-6 app-card">
      <v-card-title class="p-lg">
        <v-avatar color="primary" size="32" class="me-3">
          <v-icon icon="mdi-backup-restore" color="on-primary" size="18" />
        </v-avatar>
        <div>
          <div class="text-h6 font-weight-bold">备份操作</div>
          <div class="text-body-2 text-medium-emphasis">创建和导入数据备份</div>
        </div>
      </v-card-title>

      <v-card-text class="p-lg pt-0">
        <v-row>
          <!-- 创建备份 -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="h-100 app-card">
              <v-card-title class="text-h6 p-lg">
                <v-avatar color="success" size="24" class="me-2">
                  <v-icon icon="mdi-database-export" color="on-success" size="14" />
                </v-avatar>
                创建备份
              </v-card-title>
              <v-card-text class="p-lg pt-0">
                <v-select
                  v-model="backupFormat"
                  :items="formatOptions"
                  label="备份格式"
                  variant="outlined"
                  density="compact"
                  class="mb-3"
                />
                <v-checkbox
                  v-model="includeMetadata"
                  label="包含元数据信息"
                  density="compact"
                />
              </v-card-text>
              <v-card-actions>
                <v-btn
                  color="primary"
                  prepend-icon="mdi-backup-restore"
                  @click="createBackup"
                  :loading="creating"
                  block
                  class="app-button"
                >
                  一键备份
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
          
          <!-- 导入备份 -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="h-100 app-card">
              <v-card-title class="text-h6 p-lg">
                <v-avatar color="warning" size="24" class="me-2">
                  <v-icon icon="mdi-database-import" color="on-warning" size="14" />
                </v-avatar>
                导入备份
              </v-card-title>
              <v-card-text class="p-lg pt-0">
                <v-file-input
                  v-model="uploadFile"
                  label="选择备份文件"
                  accept=".sql,.json"
                  variant="outlined"
                  density="compact"
                  prepend-icon="mdi-file-upload"
                  show-size
                  class="mb-3"
                />
                <v-alert
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="text-caption"
                >
                  导入备份将覆盖当前数据，请谨慎操作
                </v-alert>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  color="warning"
                  prepend-icon="mdi-upload"
                  @click="uploadBackup"
                  :loading="uploading"
                  :disabled="!uploadFile"
                  block
                  class="app-button"
                >
                  上传并导入
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 备份文件列表 - 统一设计 -->
    <v-card class="app-card app-table">
      <v-card-title class="p-lg">
        <v-avatar color="info" size="32" class="me-3">
          <v-icon icon="mdi-folder-multiple" color="on-info" size="18" />
        </v-avatar>
        <div class="flex-grow-1">
          <div class="text-h6 font-weight-bold">备份文件管理</div>
          <div class="text-body-2 text-medium-emphasis">管理所有备份文件</div>
        </div>
        <v-btn
          icon="mdi-refresh"
          variant="text"
          @click="loadBackups"
          :loading="loading"
          title="刷新列表"
          class="app-button"
        />
      </v-card-title>

      <v-card-text class="p-lg pt-0">
        <!-- 备份文件表格 -->
        <v-data-table
          :headers="headers"
          :items="backups"
          :loading="loading"
          class="elevation-0"
          item-value="filename"
        >
          <!-- 文件名列 -->
          <template #item.filename="{ item }">
            <div class="d-flex align-center">
              <v-icon
                :icon="getFileIcon(item.format)"
                :color="getFileColor(item.format)"
                class="me-2"
              />
              <div>
                <div class="font-weight-medium">{{ item.filename }}</div>
                <div class="text-caption text-medium-emphasis">
                  {{ item.format }} 格式
                </div>
              </div>
            </div>
          </template>

          <!-- 大小列 -->
          <template #item.size_formatted="{ item }">
            <v-chip size="small" variant="tonal" color="info" class="app-chip">
              {{ item.size_formatted }}
            </v-chip>
          </template>

          <!-- 状态列 -->
          <template #item.is_valid="{ item }">
            <v-chip
              size="small"
              :color="item.is_valid ? 'success' : 'error'"
              variant="tonal"
              class="app-chip"
            >
              {{ item.is_valid ? '有效' : '无效' }}
            </v-chip>
          </template>

          <!-- 操作列 -->
          <template #item.actions="{ item }">
            <div class="d-flex ga-1">
              <v-btn
                icon="mdi-information"
                size="small"
                variant="text"
                @click="showBackupInfo(item)"
                title="查看详情"
              />
              <v-btn
                icon="mdi-download"
                size="small"
                variant="text"
                color="primary"
                @click="downloadBackup(item.filename)"
                title="下载"
              />
              <v-btn
                icon="mdi-restore"
                size="small"
                variant="text"
                color="warning"
                @click="confirmRestore(item)"
                :disabled="!item.is_valid"
                title="恢复"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="confirmDelete(item)"
                title="删除"
              />
            </div>
          </template>

          <!-- 无数据状态 -->
          <template #no-data>
            <div class="text-center pa-8">
              <v-icon size="64" class="mb-4 text-medium-emphasis">mdi-folder-open</v-icon>
              <div class="text-h6 text-medium-emphasis">暂无备份文件</div>
              <div class="text-subtitle-2 text-medium-emphasis mb-4">
                点击上方"一键备份"按钮创建第一个备份
              </div>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- 备份详情对话框 -->
    <v-dialog v-model="showInfoDialog" max-width="600px">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-information" class="me-3" />
          备份文件详情
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showInfoDialog = false"
          />
        </v-card-title>
        
        <v-card-text v-if="selectedBackup">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedBackup.filename"
                label="文件名"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedBackup.format"
                label="格式"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedBackup.size_formatted"
                label="文件大小"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedBackup.created_time"
                label="创建时间"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-text-field
                :model-value="selectedBackup.path"
                label="文件路径"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 确认恢复对话框 -->
    <v-dialog v-model="showRestoreDialog" max-width="500px">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-alert" class="me-3" />
          确认恢复备份
        </v-card-title>
        
        <v-card-text>
          <v-alert type="warning" variant="tonal" class="mb-4">
            <strong>警告：</strong>恢复备份将完全覆盖当前数据库中的所有数据，此操作不可撤销！
          </v-alert>
          
          <p>您确定要恢复以下备份文件吗？</p>
          <p><strong>文件名：</strong>{{ restoreTarget?.filename }}</p>
          <p><strong>创建时间：</strong>{{ restoreTarget?.created_time }}</p>
          <p><strong>文件大小：</strong>{{ restoreTarget?.size_formatted }}</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showRestoreDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="warning"
            variant="filled"
            @click="restoreBackup"
            :loading="restoring"
          >
            确认恢复
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 确认删除对话框 -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-delete" class="me-3" />
          确认删除
        </v-card-title>
        
        <v-card-text>
          <p>您确定要删除备份文件吗？</p>
          <p><strong>{{ deleteTarget?.filename }}</strong></p>
          <p class="text-caption text-medium-emphasis">此操作不可撤销</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDeleteDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="filled"
            @click="deleteBackup"
            :loading="deleting"
          >
            确认删除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const uploading = ref(false)
const restoring = ref(false)
const deleting = ref(false)

const backups = ref([])
const backupFormat = ref('sql')
const includeMetadata = ref(true)
const uploadFile = ref(null)

const showInfoDialog = ref(false)
const showRestoreDialog = ref(false)
const showDeleteDialog = ref(false)

const selectedBackup = ref(null)
const restoreTarget = ref(null)
const deleteTarget = ref(null)

// 配置选项
const formatOptions = [
  { value: 'sql', title: 'SQL 格式 (.sql)' },
  { value: 'json', title: 'JSON 格式 (.json)' }
]

// 表格头部
const headers = [
  { title: '文件名', key: 'filename', sortable: true },
  { title: '大小', key: 'size_formatted', sortable: false },
  { title: '创建时间', key: 'created_time', sortable: true },
  { title: '修改时间', key: 'modified_time', sortable: true },
  { title: '状态', key: 'is_valid', sortable: false },
  { title: '操作', key: 'actions', sortable: false, width: '200px' }
]

// 方法
const loadBackups = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/backup/list')

    if (response.data.success) {
      backups.value = response.data.backups
    } else {
      throw new Error(response.data.message)
    }
  } catch (error) {
    console.error('加载备份列表失败:', error)
    // 这里可以添加错误提示
  } finally {
    loading.value = false
  }
}

const createBackup = async () => {
  try {
    creating.value = true

    const response = await axios.post('/api/backup/create', {
      format: backupFormat.value,
      include_metadata: includeMetadata.value
    })

    if (response.data.success) {
      // 显示成功消息
      console.log('备份创建成功:', response.data.message)

      // 刷新备份列表
      await loadBackups()
    } else {
      throw new Error(response.data.message)
    }
  } catch (error) {
    console.error('创建备份失败:', error)
    // 这里可以添加错误提示
  } finally {
    creating.value = false
  }
}

const uploadBackup = async () => {
  if (!uploadFile.value) return

  try {
    uploading.value = true

    // 上传文件
    const formData = new FormData()
    formData.append('file', uploadFile.value[0])

    const uploadResponse = await axios.post('/api/backup/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (uploadResponse.data.success) {
      // 自动恢复上传的备份
      const restoreResponse = await axios.post('/api/backup/restore', {
        backup_filename: uploadResponse.data.filename
      })

      if (restoreResponse.data.success) {
        console.log('备份恢复成功:', restoreResponse.data.message)

        // 清空文件选择
        uploadFile.value = null

        // 刷新备份列表
        await loadBackups()
      } else {
        throw new Error(restoreResponse.data.message)
      }
    } else {
      throw new Error(uploadResponse.data.message)
    }
  } catch (error) {
    console.error('上传并导入备份失败:', error)
    // 这里可以添加错误提示
  } finally {
    uploading.value = false
  }
}

const showBackupInfo = async (backup) => {
  try {
    const response = await axios.get(`/api/backup/info/${backup.filename}`)

    if (response.data.success) {
      selectedBackup.value = response.data
      showInfoDialog.value = true
    } else {
      throw new Error(response.data.message)
    }
  } catch (error) {
    console.error('获取备份信息失败:', error)
    // 这里可以添加错误提示
  }
}

const downloadBackup = (filename) => {
  const url = `/api/backup/download/${filename}`
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const confirmRestore = (backup) => {
  restoreTarget.value = backup
  showRestoreDialog.value = true
}

const restoreBackup = async () => {
  if (!restoreTarget.value) return

  try {
    restoring.value = true

    const response = await axios.post('/api/backup/restore', {
      backup_filename: restoreTarget.value.filename
    })

    if (response.data.success) {
      console.log('备份恢复成功:', response.data.message)

      // 关闭对话框
      showRestoreDialog.value = false
      restoreTarget.value = null

      // 刷新备份列表
      await loadBackups()
    } else {
      throw new Error(response.data.message)
    }
  } catch (error) {
    console.error('恢复备份失败:', error)
    // 这里可以添加错误提示
  } finally {
    restoring.value = false
  }
}

const confirmDelete = (backup) => {
  deleteTarget.value = backup
  showDeleteDialog.value = true
}

const deleteBackup = async () => {
  if (!deleteTarget.value) return

  try {
    deleting.value = true

    const response = await axios.delete(`/api/backup/delete/${deleteTarget.value.filename}`)

    if (response.data.success) {
      console.log('备份删除成功:', response.data.message)

      // 关闭对话框
      showDeleteDialog.value = false
      deleteTarget.value = null

      // 刷新备份列表
      await loadBackups()
    } else {
      throw new Error(response.data.message)
    }
  } catch (error) {
    console.error('删除备份失败:', error)
    // 这里可以添加错误提示
  } finally {
    deleting.value = false
  }
}

const getFileIcon = (format) => {
  switch (format?.toLowerCase()) {
    case 'sql':
      return 'mdi-database'
    case 'json':
      return 'mdi-code-json'
    default:
      return 'mdi-file'
  }
}

const getFileColor = (format) => {
  switch (format?.toLowerCase()) {
    case 'sql':
      return 'blue'
    case 'json':
      return 'green'
    default:
      return 'grey'
  }
}

// 生命周期
onMounted(() => {
  loadBackups()
})
</script>

<style scoped>
/* BackupManager 统一设计样式 */
.v-card.app-card {
  transition: var(--transition-normal);
}

.v-card.app-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 文件图标样式 */
.v-icon {
  transition: var(--transition-fast);
}

/* 操作按钮样式现在通过main.js的VBtn defaults配置管理 */
</style>
