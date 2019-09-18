import 'regenerator-runtime/runtime';

async function start() {
    const { pathname } = location;
    const [, locale, , ...rest] = pathname.split('/');
    const { documentData } = await fetch(
        '/api/v1/doc/' + locale + '/' + rest.join('/')
    ).then(r => r.json());
    window._react_data = {
        locale,
        stringCatalog: {},
        pluralExpression: () => null,
        documentData,
        url: pathname
    };
    await import('../kuma/javascript/src/index.jsx');
}

start().catch(e => console.error(e));
