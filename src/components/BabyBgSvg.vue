<template>
  <svg
    class="baby-bg"
    xmlns="http://www.w3.org/2000/svg"
    preserveAspectRatio="xMidYMid slice"
    viewBox="0 0 1440 900"
  >
    <defs>
      <!-- 大面积柔和渐变 -->
      <radialGradient id="bgGlow1" cx="30%" cy="40%" r="60%">
        <stop offset="0%" stop-color="#ffe4ec" />
        <stop offset="100%" stop-color="#f0f4ff" stop-opacity="0" />
      </radialGradient>
      <radialGradient id="bgGlow2" cx="75%" cy="55%" r="55%">
        <stop offset="0%" stop-color="#dbeaff" />
        <stop offset="100%" stop-color="#fff5f9" stop-opacity="0" />
      </radialGradient>
      <radialGradient id="bgGlow3" cx="50%" cy="85%" r="40%">
        <stop offset="0%" stop-color="#fff3d6" />
        <stop offset="100%" stop-color="#f5f0ff" stop-opacity="0" />
      </radialGradient>
    </defs>

    <!-- 底色 -->
    <rect width="1440" height="900" fill="#f8f0f5" />
    <rect width="1440" height="900" fill="url(#bgGlow1)" />
    <rect width="1440" height="900" fill="url(#bgGlow2)" />
    <rect width="1440" height="900" fill="url(#bgGlow3)" />

    <!-- ========== 左上角：泰迪熊 ========== -->
    <g transform="translate(90,100) scale(0.9)" opacity="0.82">
      <!-- 耳朵 -->
      <circle cx="30" cy="20" r="18" fill="#f5d5c0" stroke="#e8b89e" stroke-width="2" />
      <circle cx="30" cy="20" r="9" fill="#f9c4a8" />
      <circle cx="90" cy="20" r="18" fill="#f5d5c0" stroke="#e8b89e" stroke-width="2" />
      <circle cx="90" cy="20" r="9" fill="#f9c4a8" />
      <!-- 头 -->
      <circle cx="60" cy="50" r="38" fill="#f5d5c0" stroke="#e8b89e" stroke-width="2" />
      <!-- 脸中心 -->
      <ellipse cx="60" cy="60" rx="18" ry="14" fill="#fce8d8" />
      <!-- 眼 -->
      <circle cx="47" cy="47" r="4" fill="#5a4a42" />
      <circle cx="73" cy="47" r="4" fill="#5a4a42" />
      <circle cx="48.5" cy="45.5" r="1.5" fill="#fff" />
      <circle cx="74.5" cy="45.5" r="1.5" fill="#fff" />
      <!-- 鼻 -->
      <ellipse cx="60" cy="56" rx="5" ry="3.5" fill="#d4978a" />
      <!-- 嘴 -->
      <path d="M55 61 Q60 67 65 61" fill="none" stroke="#d4978a" stroke-width="1.5" stroke-linecap="round" />
      <!-- 蝴蝶结 -->
      <path d="M48 80 Q40 72 38 82 Q40 90 48 84 Z" fill="#ffb6c8" stroke="#f59ab2" stroke-width="1" />
      <path d="M72 80 Q80 72 82 82 Q80 90 72 84 Z" fill="#ffb6c8" stroke="#f59ab2" stroke-width="1" />
      <circle cx="60" cy="82" r="4" fill="#ff9ab5" />
      <!-- 身体 -->
      <ellipse cx="60" cy="116" rx="32" ry="28" fill="#f5d5c0" stroke="#e8b89e" stroke-width="2" />
    </g>

    <!-- ========== 右上角：奶瓶 ========== -->
    <g transform="translate(1200,60) rotate(15)" opacity="0.78">
      <!-- 瓶身 -->
      <rect x="10" y="40" width="50" height="90" rx="12" fill="#fffde8" stroke="#f0e6a0" stroke-width="2" />
      <!-- 刻度 -->
      <line x1="18" y1="55" x2="30" y2="55" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="65" x2="35" y2="65" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="75" x2="30" y2="75" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="85" x2="35" y2="85" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="95" x2="30" y2="95" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="105" x2="35" y2="105" stroke="#e8d88c" stroke-width="1" />
      <!-- 奶嘴头 -->
      <path d="M20 40 Q35 10 50 40" fill="#ffd6a0" stroke="#f0c080" stroke-width="2" />
      <!-- 盖 -->
      <rect x="15" y="36" width="40" height="8" rx="3" fill="#b8e6d0" stroke="#8fd4b0" stroke-width="1.5" />
      <!-- 把手 -->
      <path d="M60 60 Q80 70 60 100" fill="none" stroke="#e8d88c" stroke-width="5" stroke-linecap="round" />
    </g>

    <!-- ========== 左中：摇铃 ========== -->
    <g transform="translate(60, 440) rotate(-12)" opacity="0.75">
      <!-- 手柄 -->
      <rect x="28" y="50" width="10" height="40" rx="5" fill="#ffd6a0" stroke="#f0c080" stroke-width="1.5" />
      <!-- 铃球 -->
      <circle cx="33" cy="30" r="26" fill="#ffc8d8" stroke="#f5a0b8" stroke-width="2" />
      <circle cx="33" cy="30" r="15" fill="#ffe0ea" />
      <!-- 笑脸 -->
      <circle cx="26" cy="27" r="2.5" fill="#6a5a52" />
      <circle cx="40" cy="27" r="2.5" fill="#6a5a52" />
      <path d="M27 35 Q33 40 39 35" fill="none" stroke="#e08898" stroke-width="1.5" stroke-linecap="round" />
    </g>

    <!-- ========== 右下角：另一个奶瓶（小、倾斜） ========== -->
    <g transform="translate(1250,650) rotate(-25) scale(0.7)" opacity="0.68">
      <rect x="10" y="40" width="50" height="90" rx="12" fill="#fffde8" stroke="#f0e6a0" stroke-width="2" />
      <line x1="18" y1="60" x2="35" y2="60" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="75" x2="30" y2="75" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="90" x2="35" y2="90" stroke="#e8d88c" stroke-width="1" />
      <line x1="18" y1="105" x2="30" y2="105" stroke="#e8d88c" stroke-width="1" />
      <path d="M20 40 Q35 10 50 40" fill="#ffd6a0" stroke="#f0c080" stroke-width="2" />
      <rect x="15" y="36" width="40" height="8" rx="3" fill="#a8d8f0" stroke="#88c4e0" stroke-width="1.5" />
    </g>

    <!-- ========== 中上：牙胶圈 ========== -->
    <g transform="translate(420, 50)" opacity="0.72">
      <circle cx="40" cy="40" r="30" fill="none" stroke="#ffc0d0" stroke-width="10" stroke-linecap="round" stroke-dasharray="20 12" />
      <circle cx="40" cy="10" r="8" fill="#a8e0f0" />
      <circle cx="66" cy="22" r="8" fill="#ffe0a0" />
      <circle cx="14" cy="22" r="8" fill="#d0f0c0" />
    </g>

    <!-- ========== 右中：摇铃（另一个） ========== -->
    <g transform="translate(1300,370) rotate(20) scale(0.8)" opacity="0.7">
      <rect x="25" y="55" width="12" height="35" rx="6" fill="#c8e8a0" stroke="#a8d080" stroke-width="1.5" />
      <circle cx="31" cy="32" r="24" fill="#ffe0a0" stroke="#f0cc70" stroke-width="2" />
      <circle cx="31" cy="32" r="14" fill="#fff0c8" />
      <circle cx="25" cy="29" r="2" fill="#6a5a52" />
      <circle cx="37" cy="29" r="2" fill="#6a5a52" />
      <path d="M25 37 Q31 42 37 37" fill="none" stroke="#d0a060" stroke-width="1.5" stroke-linecap="round" />
      <!-- 星形顶部 -->
      <polygon points="31,2 34,11 43,11 36,17 38,26 31,21 24,26 26,17 19,11 28,11" fill="#ffe880" stroke="#f0d860" stroke-width="1" />
    </g>

    <!-- ========== 左下：成长记录本 ========== -->
    <g transform="translate(160,620) rotate(5)" opacity="0.72">
      <!-- 封面 -->
      <rect x="0" y="0" width="130" height="95" rx="6" fill="#d8ecff" stroke="#b0d0f0" stroke-width="2" />
      <rect x="8" y="8" width="114" height="79" rx="4" fill="#fff" stroke="#dde8f4" stroke-width="1" />
      <!-- 标题 -->
      <text x="65" y="30" text-anchor="middle" fill="#7eb8e0" font-size="11" font-weight="600" font-family="sans-serif">Baby Book</text>
      <!-- 封面小宝宝 -->
      <circle cx="45" cy="58" r="12" fill="#ffe0c8" stroke="#f0c8a8" stroke-width="1" />
      <circle cx="41" cy="55" r="1.5" fill="#5a4a42" />
      <circle cx="49" cy="55" r="1.5" fill="#5a4a42" />
      <path d="M43 61 Q45 64 47 61" fill="none" stroke="#e0a090" stroke-width="1" stroke-linecap="round" />
      <!-- 封面小星星 -->
      <polygon points="80,48 82,54 88,54 83,58 85,64 80,60 75,64 77,58 72,54 78,54" fill="#ffe880" stroke="#f0d860" stroke-width="0.8" />
      <!-- 封面小爱心 -->
      <path d="M90 72 Q90 66 96 66 Q102 66 102 72 Q102 80 96 86 Q90 80 90 72 Z" fill="#ffb0c0" opacity="0.7" />
    </g>

    <!-- ========== 散落的小星星 ========== -->
    <g opacity="0.6">
      <polygon points="320,180 323,190 333,190 325,196 328,206 320,200 312,206 315,196 307,190 317,190" fill="#ffe880" />
      <polygon points="1100,150 1102,157 1109,157 1104,161 1106,168 1100,164 1094,168 1096,161 1091,157 1098,157" fill="#ffe880" />
      <polygon points="700,80 702,87 709,87 704,91 706,98 700,94 694,98 696,91 691,87 698,87" fill="#ffd088" />
      <polygon points="200,350 202,357 209,357 204,361 206,368 200,364 194,368 196,361 191,357 198,357" fill="#ffe880" />
      <polygon points="1350,500 1352,507 1359,507 1354,511 1356,518 1350,514 1344,518 1346,511 1341,507 1348,507" fill="#ffe880" />
      <polygon points="580,770 582,777 589,777 584,781 586,788 580,784 574,788 576,781 571,777 578,777" fill="#ffd088" />
      <polygon points="950,820 952,827 959,827 954,831 956,838 950,834 944,838 946,831 941,827 948,827" fill="#ffe880" />
    </g>

    <!-- ========== 散落的小爱心 ========== -->
    <g opacity="0.5">
      <path d="M500 130 Q500 122 508 122 Q516 122 516 130 Q516 140 508 148 Q500 140 500 130 Z" fill="#ffc0d0" />
      <path d="M1060 280 Q1060 272 1068 272 Q1076 272 1076 280 Q1076 290 1068 298 Q1060 290 1060 280 Z" fill="#ffb0c0" />
      <path d="M250 560 Q250 553 257 553 Q264 553 264 560 Q264 568 257 575 Q250 568 250 560 Z" fill="#ffc8d8" />
      <path d="M1180 740 Q1180 733 1187 733 Q1194 733 1194 740 Q1194 748 1187 755 Q1180 748 1180 740 Z" fill="#ffc0d0" />
      <path d="M850 110 Q850 103 857 103 Q864 103 864 110 Q864 118 857 125 Q850 118 850 110 Z" fill="#ffd0e0" />
    </g>

    <!-- ========== 小圆点装饰 ========== -->
    <g opacity="0.35">
      <circle cx="400" cy="300" r="4" fill="#ffc8d8" />
      <circle cx="650" cy="150" r="3" fill="#c8e8ff" />
      <circle cx="900" cy="400" r="5" fill="#ffe0a0" />
      <circle cx="1100" cy="600" r="4" fill="#d0f0c0" />
      <circle cx="300" cy="700" r="3" fill="#ffc8d8" />
      <circle cx="750" cy="800" r="4" fill="#c8e8ff" />
      <circle cx="1000" cy="100" r="3" fill="#ffe0a0" />
      <circle cx="180" cy="250" r="3.5" fill="#d0e8ff" />
      <circle cx="1380" cy="250" r="3" fill="#ffd8e8" />
      <circle cx="550" cy="600" r="3.5" fill="#d0f0c0" />
    </g>

    <!-- ========== 中下偏右：奶嘴 ========== -->
    <g transform="translate(1050,700) rotate(10)" opacity="0.65">
      <!-- 盾 -->
      <ellipse cx="30" cy="25" rx="28" ry="18" fill="#ffc8e0" stroke="#f0a0c0" stroke-width="2" />
      <!-- 盾高光 -->
      <ellipse cx="22" cy="20" rx="10" ry="6" fill="#ffe0f0" opacity="0.6" />
      <!-- 环 -->
      <circle cx="30" cy="10" r="8" fill="none" stroke="#f0a0c0" stroke-width="3" />
      <!-- 奶嘴头 -->
      <ellipse cx="30" cy="48" rx="10" ry="12" fill="#ffe0c8" stroke="#f0c0a0" stroke-width="1.5" />
    </g>

    <!-- ========== 中上偏左：云朵 ========== -->
    <g transform="translate(620,60)" opacity="0.4">
      <ellipse cx="40" cy="30" rx="30" ry="18" fill="#fff" />
      <ellipse cx="65" cy="25" rx="22" ry="15" fill="#fff" />
      <ellipse cx="20" cy="28" rx="18" ry="12" fill="#fff" />
    </g>
    <g transform="translate(900,30)" opacity="0.3">
      <ellipse cx="30" cy="25" rx="24" ry="14" fill="#fff" />
      <ellipse cx="52" cy="22" rx="18" ry="12" fill="#fff" />
      <ellipse cx="14" cy="23" rx="14" ry="10" fill="#fff" />
    </g>

    <!-- ========== 下方中间：脚印 ========== -->
    <g transform="translate(720,780) rotate(-15)" opacity="0.35">
      <ellipse cx="10" cy="20" rx="8" ry="12" fill="#ffc8d8" />
      <circle cx="4" cy="6" r="3.5" fill="#ffc8d8" />
      <circle cx="14" cy="4" r="3" fill="#ffc8d8" />
      <circle cx="22" cy="8" r="2.5" fill="#ffc8d8" />
    </g>
    <g transform="translate(770,800) rotate(-5)" opacity="0.3">
      <ellipse cx="10" cy="20" rx="8" ry="12" fill="#ffc8d8" />
      <circle cx="4" cy="6" r="3.5" fill="#ffc8d8" />
      <circle cx="14" cy="4" r="3" fill="#ffc8d8" />
      <circle cx="22" cy="8" r="2.5" fill="#ffc8d8" />
    </g>
  </svg>
</template>

<style scoped>
.baby-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}
</style>
