document.addEventListener('DOMContentLoaded', function () {
  const menuBtn = document.getElementById('menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  menuBtn.addEventListener('click', function () {
    mobileMenu.classList.toggle('hidden');
  });
});

document.getElementById('search-btn').addEventListener('click', function () {
    const searchInput = document.getElementById('search-input');
  
    if (searchInput.classList.contains('hidden')) {
      searchInput.classList.remove('hidden');
      searchInput.classList.add('block'); 
      searchInput.focus();
    } else {
      searchInput.classList.remove('block');
      searchInput.classList.add('hidden');
    }
  });
  
  