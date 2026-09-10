/**
 * Shared v=2 helpers: mark body + keep navbar/footer links inside the v2 experience.
 */
(function () {
    document.body.classList.add('v2-site');

    function isV2Path(pathname) {
        const path = (pathname || '/').replace(/\/$/, '') || '/';
        return (
            path === '/' ||
            path === '/listings' ||
            path.startsWith('/listings/') ||
            path === '/about' ||
            path === '/investor-services' ||
            path === '/vector-highlights'
        );
    }

    function withV2(href) {
        try {
            const url = new URL(href, window.location.origin);
            if (url.origin !== window.location.origin) return href;
            if (!isV2Path(url.pathname)) return href;
            url.searchParams.set('v', '2');
            return url.pathname + url.search + url.hash;
        } catch (e) {
            return href;
        }
    }

    document.querySelectorAll('.navbar a[href], footer a[href]').forEach((link) => {
        link.href = withV2(link.href);
    });
})();
