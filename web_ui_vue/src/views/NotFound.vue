<template>
  <div class="d-flex flex-column align-center justify-center" style="min-height: 60vh;">
    <v-icon size="120" color="primary" class="mb-4">
      mdi-spider-web
    </v-icon>
    
    <h1 class="text-h3 font-weight-bold text-primary mb-2">
      404
    </h1>
    
    <h2 class="text-h5 text-medium-emphasis mb-4">
      页面未找到
    </h2>
    
    <p class="text-subtitle-1 text-center text-medium-emphasis mb-6" style="max-width: 400px;">
      抱歉，您访问的页面不存在。可能是链接错误或页面已被移动。
    </p>
    
    <div class="d-flex ga-4">
      <v-btn
        color="primary"
        size="large"
        prepend-icon="mdi-home"
        @click="$router.push('/')"
      >
        返回首页
      </v-btn>
      
      <v-btn
        variant="outlined"
        size="large"
        prepend-icon="mdi-arrow-left"
        @click="$router.go(-1)"
      >
        返回上页
      </v-btn>
    </div>
  </div>
</template>

<script setup>
// 404页面不需要额外的逻辑
</script>
