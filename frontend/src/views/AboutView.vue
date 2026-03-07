<template>
  <section class="about">
    <h1 class="about__title">
      關於 NCU TLDR
    </h1>
    <p class="about__text">
      NCU TLDR 是給中央大學同學快速掌握課程資訊的評價平台，重點是讓選課前的資訊更透明、決策更快。
    </p>
    <p class="about__text">
      我們聚焦在「評分、心得、許願池」三件事，並逐步把功能串接到正式後端 API。
    </p>
  </section>
</template>

<style scoped>
.about {
  max-width: 720px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.about__title {
  margin-bottom: var(--spacing-md);
}

.about__text {
  margin-bottom: var(--spacing-md);
  line-height: 1.8;
}
</style>
