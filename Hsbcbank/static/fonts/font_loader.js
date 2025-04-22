// Font loader for multilingual support
// This script dynamically loads the required fonts based on the selected language

document.addEventListener('DOMContentLoaded', function() {
    // Define font URLs
    const fonts = {
        'noto-sans': 'https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap',
        'noto-sans-tamil': 'https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;700&display=swap',
        'noto-sans-devanagari': 'https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap'
    };
    
    // Load all fonts by default
    loadFonts();
    
    // Listen for language tab changes to ensure appropriate fonts are loaded
    const languageTabs = document.querySelectorAll('.nav-link[data-language]');
    languageTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const language = this.getAttribute('data-language');
            loadFontsByLanguage(language);
        });
    });
    
    // Function to load all fonts
    function loadFonts() {
        Object.values(fonts).forEach(fontUrl => {
            const linkElement = document.createElement('link');
            linkElement.rel = 'stylesheet';
            linkElement.href = fontUrl;
            document.head.appendChild(linkElement);
        });
    }
    
    // Function to load fonts based on selected language
    function loadFontsByLanguage(language) {
        let fontUrl;
        
        switch(language) {
            case 'ta':
                fontUrl = fonts['noto-sans-tamil'];
                break;
            case 'hi':
                fontUrl = fonts['noto-sans-devanagari'];
                break;
            case 'en':
            default:
                fontUrl = fonts['noto-sans'];
                break;
        }
        
        // Check if the font is already loaded
        const existingLink = document.querySelector(`link[href="${fontUrl}"]`);
        if (!existingLink) {
            const linkElement = document.createElement('link');
            linkElement.rel = 'stylesheet';
            linkElement.href = fontUrl;
            document.head.appendChild(linkElement);
        }
    }
    
    // Apply font to form elements based on language
    function applyFontToElements(language) {
        const tabContent = document.getElementById(`${language}-content`);
        if (!tabContent) return;
        
        let fontFamily;
        
        switch(language) {
            case 'ta':
                fontFamily = "'Noto Sans Tamil', sans-serif";
                break;
            case 'hi':
                fontFamily = "'Noto Sans Devanagari', sans-serif";
                break;
            case 'en':
            default:
                fontFamily = "'Noto Sans', sans-serif";
                break;
        }
        
        tabContent.style.fontFamily = fontFamily;
    }
    
    // Apply fonts to initial tab content
    const languages = ['en', 'ta', 'hi'];
    languages.forEach(lang => {
        applyFontToElements(lang);
    });
});
