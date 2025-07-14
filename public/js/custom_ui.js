// 等待 DOM 完全加载
document.addEventListener('DOMContentLoaded', function() {
    // 查找 README 按钮并隐藏它
    const readmeButton = document.querySelector('readme-button');
    if (readmeButton) {
        readmeButton.style.display = 'none';
    }
});
