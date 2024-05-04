import { IconArticle } from '@tabler/icons-react';

const icon = { IconArticle };

const log = {
    id: 'logD',
    title: 'Log',
    type: 'group',
    children: [
        {
            id: 'log',
            title: 'Logs',
            type: 'item',
            url: '/status',
            icon: icon.IconArticle,
            breadcrumbs: false
        }
    ]
}

export default log