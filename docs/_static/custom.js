// Select the button using its class, assuming it's the only one with this class
const nav = document.querySelector(".flex.items-center.space-x-1");
console.log(nav);

const themeToggleButton = nav.childNodes[3];
console.log(themeToggleButton);

mode = localStorage.getItem('darkMode');
setTheme(mode);

// Add an event listener to the button
themeToggleButton.addEventListener('click', function() {
    mode = mode === 'light' ? 'dark' : 'light'
    setTheme(mode);
});

function setTheme(mode) {
    var pres = document.body.getElementsByTagName("pre");
    for (let pre of pres) {
        if (mode === 'dark') {
            pre.classList.add('dark-theme');
            pre.classList.remove('light-theme');
        } else {
            pre.classList.add('light-theme');
            pre.classList.remove('dark-theme');
        }
    }
}
