from pandas.io.formats.style import jinja2

daily_report = jinja2.Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Visit report {{hcp.name}} - {{visit_date}}</title>
</head>
<style>
@page {
    size: A4;
    margin: 0 auto;
}

* {
    box-sizing: border-box;
}

html, body {
    width: 210mm;
    height: 297mm;
    margin: 0 auto;
}

body {
    font-family: Inter, sans-serif;
    font-size: 14px;
    line-height: 1.4;
    color: #1A1C21;
}

body a {
    color: inherit;
    text-decoration: none;
}

.round-box:not(table) {
    display: flex;
    align-items: flex-start;
    padding: 10px 14px;
    border-radius: 8px;
    text-decoration: none;
}

table.round-box {
    border-radius: 8px;
}

table.round-box td {
    padding-top: 10px;
    padding-bottom: 10px;
}

table.round-box td:first-child {
    padding-left: 14px;
}

table.round-box td:last-child {
    padding-right: 14px;
}

table.round-box td:nth-child(2) {
    padding-left: 8px;
}

.round-box--success {
    background-color: #DEFAF7;
    color: #009484;
}

.round-box--secondary {
    background-color: #DEE2FA;
    color: #002994;
}

.round-box--warning {
    background-color: #FAE1CF;
    color: #E46A11;
}

.icon-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon {
    flex: 0 0 auto;
    display: block;
    width: 20px;
    height: 20px;
}

.card {
    border: 1px solid #E0E2E7;
    border-radius: 8px;
    box-shadow: 0 1.5px 2px 0 #1018281A;
}

.card__table-header-wrapper {
    padding: 18px 20px;
}

.card__table-header {
    display: grid;
    grid-template-columns: auto 1fr auto auto;
    gap: 12px;
    align-items: center;
}

.card-inner {
    padding: 20px;
}

.card-price {
    font-size: 24px;
    line-height: 32px;
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.card-title {
    margin-bottom: 8px;
    color: #667085;
    font-size: 16px;
    line-height: 24px;
}

.card-footer {
    display: flex;
    align-items: center;
    gap: 8px;
}

.badge {
    display: inline;
    padding: 2px 6px;
    border-radius: 100px;
    font-weight: 600;
    font-size: 12px;
    line-height: 18px;
}

.color-secondary {
    color: #667085;
}

.badge--success {
    color: #0D894F;
    background-color: #E7F4EE;
}

.badge--danger {
    color: #F04438;
    background-color: #FEEDEC;
}

.badge--neutral {
    color: #667085;
    background-color: #F0F1F3;
}

.dot {
    display: inline-block;
    width: 4px;
    height: 4px;
    background-color: #C2C6CE;
    border-radius: 50%;
}

hr {
    margin: 1em 0;
    border: 1px solid #f0f1f3;
    border-bottom: none;
}

.table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
    color: #333843;
}

.table th,
.table td {
    padding: 18px 20px;
    border-bottom: 1px solid #F0F1F3;
    text-align: left;
}

.table tbody tr:last-child td {
    border-bottom: none;
}

.table th {
    background-color: #F9F9FC;
    font-weight: 500;
}

ul {
    margin: 0;
    padding-left: 20px;
}

ul li + li {
    margin-top: 20px;
}

.avoid-page-break-inside {
    page-break-inside: avoid
}

header,
footer {
    position: fixed;
}

header {
    padding: .5cm;
    background: #fff;
}

.header-space {
    height: 110px;
}

.footer-space {
    height: 130px;
}

header {
    top: 0;
    right: 0;
    left: 0;
}

footer {
    right: 0;
    bottom: 0;
    left: 0;
}

main {
    padding: 0 .5cm;
}

.no-split {
    page-break-inside: avoid;
}

.heading {
    display: grid;
    align-items: flex-start;
    gap: 16px;
}
</style>
<body>
<div>
    <div>
        <header>
            <div style="float: left; text-align: left; width: 134px;">
                <h4 style="color: #876000">Confidential</h4>
            </div>
            <div style="position: absolute; left: 0; right: 0;">
                <h4 style="color: red; text-align: center">PRERELEASE VERSION - FOR TESTING AND DEMO</h4>
            </div>
            <div style="text-align: right;">
                <svg style="width: 134px; height: 50px;" width="134" height="50" viewBox="0 0 134 50"
                     fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.5168 12.5C12.5168 9.18479 13.8356 6.00537 16.1829 3.66117C18.5303 1.31696 21.714 0 25.0337 0C28.3533 0 31.537 1.31696 33.8844 3.66117C36.2318 6.00537 37.5505 9.18479 37.5505 12.5H12.5168ZM12.5168 37.5C12.5168 34.1848 13.8356 31.0054 16.1829 28.6612C18.5303 26.317 21.714 25 25.0337 25C21.714 25 18.5303 23.683 16.1829 21.3388C13.8356 18.9946 12.5168 15.8152 12.5168 12.5C9.19716 12.5 6.01346 13.817 3.6661 16.1612C1.31873 18.5054 0 21.6848 0 25C0 28.3152 1.31873 31.4946 3.6661 33.8388C6.01346 36.183 9.19716 37.5 12.5168 37.5ZM12.5168 37.5C12.5168 40.8152 13.8356 43.9946 16.1829 46.3388C18.5303 48.683 21.714 50 25.0337 50C28.3533 50 31.537 48.683 33.8844 46.3388C36.2318 43.9946 37.5505 40.8152 37.5505 37.5H12.5168ZM25.0337 25C28.3533 25 31.537 26.317 33.8844 28.6612C36.2318 31.0054 37.5505 34.1848 37.5505 37.5C39.1942 37.5 40.8219 37.1767 42.3405 36.5485C43.8591 35.9203 45.2389 34.9996 46.4012 33.8388C47.5635 32.6781 48.4855 31.3001 49.1145 29.7835C49.7436 28.267 50.0673 26.6415 50.0673 25C50.0673 23.3585 49.7436 21.733 49.1145 20.2165C48.4855 18.6999 47.5635 17.3219 46.4012 16.1612C45.2389 15.0004 43.8591 14.0797 42.3405 13.4515C40.8219 12.8233 39.1942 12.5 37.5505 12.5C37.5505 15.8152 36.2318 18.9946 33.8844 21.3388C31.537 23.683 28.3533 25 25.0337 25Z"
                          fill="#009484"/>
                    <path d="M81.6181 12.5H89.3727V37.497H83.6241V20.6853L76.2719 37.497L68.5324 20.6641V37.497H63.1711V12.5H70.8349L76.3627 25.4381L81.6181 12.5ZM109.829 19.8846C109.829 14.9444 106.025 12.0861 101.481 12.0861C96.9366 12.0861 92.0624 14.7208 92.0624 19.8393C92.0624 24.2779 96.9548 26.5591 99.7474 27.2782C101.281 27.6831 105.151 28.1152 105.151 30.8769C105.151 33.5025 102.446 34.2186 100.422 34.2186C97.814 34.2186 96.2831 32.4057 96.507 29.635H91.3726C91.1941 35.8533 95.4268 38.1708 100.371 38.2856C106.086 38.4155 110.449 35.9772 110.449 30.481C110.449 24.9849 105.499 24.0845 101.629 22.8306C100.147 22.332 97.3632 21.8999 97.3632 19.3377C97.3632 17.2015 99.2088 16.1802 101.097 16.1802C103.517 16.1802 104.785 17.3888 104.966 19.8725H109.829M120.645 12.4607H112.667V37.4335H120.642C127.271 37.4335 134 33.6083 134 24.9698C134 16.3313 127.271 12.4728 120.642 12.4728L120.645 12.4607ZM120.285 32.8892H118.076V17.0625H120.285C126.363 17.0625 128.557 21.0207 128.557 24.9819C128.557 28.9431 126.36 32.9013 120.282 32.9013L120.285 32.8892Z"
                          fill="#243444"/>
                </svg>

            </div>
        </header>
        <table style="width: 100%;">
            <thead>
                <tr>
                    <td>
                        <div class="header-space">&nbsp;</div>
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <main>
                            <div
                                    style="display: grid; gap: 24px; margin: 0 0 30px;"
                            >
                                <div class="heading" style="grid-template-columns: auto 1fr 1fr;">
                                    <div
                                            style="width: 16px; height: 16px; margin: 7px 4px 0 0; border-radius: 4px; background-color: #009484;"
                                    ></div>
                                    <div style="flex: 1 1 auto;">
                                        <div style="margin-bottom: 7px; font-size: 20px; line-height: 30px;">
                                            Meeting with {{ hcp.name }}
                                        </div>
                                        <div
                                                class="color-secondary"
                                                style="display: flex; flex-wrap: wrap; align-items: center; font-weight: 400;"
                                        >
                                            {{ visit_date }}
                                            <span class="dot" style="margin: 0 8px;"></span>
                                            <strong>{{ account.name }}</strong>
                                        </div>
                                        <div
                                                class="color-secondary"
                                                style="display: flex; flex-wrap: wrap; align-items: center; font-weight: 400;"
                                        >
                                            MDM ID: {{ hcp.id }}
                                        </div>
                                        <div
                                                class="color-secondary"
                                                style="display: flex; flex-wrap: wrap; align-items: center; font-weight: 400;"
                                        >
                                            Specialty: {{ hcp.specialty }}
                                        </div>
                                        <div
                                                class="color-secondary"
                                                style="display: flex; flex-wrap: wrap; align-items: center; font-weight: 400;"
                                        >
                                            {% if hcp.ter_target == 'A' %}
                                                <p class="round-box round-box--warning">Account priority:&nbsp;<strong>{{ hcp.ter_target }}</strong></p>
                                            {% else %}
                                                <p class="round-box round-box--secondary">Account priority:&nbsp;<strong>{{ hcp.ter_target }}</strong></p>
                                            {% endif %}
                                        </div>
                                        <div
                                                class="color-secondary"
                                                style="display: flex; flex-wrap: wrap; align-items: center; font-weight: 400;"
                                        >
                                            <p class="round-box round-box--warning"><strong>Product priorities:</strong>&nbsp;{{ hcp.product_priorities }}</p>
                                        </div>
                                    </div>
                                    <div style="display: flex; flex-wrap: wrap; justify-content:flex-end;">
                                        <a
                                                target="_blank" href="{{account.qlik_url}}"
                                                class="round-box round-box--success"
                                        >
                                            Account360
                                        </a>
                                        <a
                                                target="_blank" href="{{hcp.qlik_url}}"
                                                class="round-box round-box--success"
                                                style="margin-left: 16px;"
                                        >
                                            HCP360
                                        </a>
                                        <a
                                                target="_blank" href="{{account.map_url}}"
                                                class="round-box round-box--warning"
                                                style="margin-left: 16px;"
                                        >
                                            Map
                                        </a>
                                    </div>
                                </div>                                    
                                    <div>
                                        <strong>Consent Information</strong>
                                      {% for consent in consents.metrics %}
                                        <p>
                                          <strong>Channel:</strong> {{ consent.channel }}, <strong>Status:</strong> {{ consent.opt_in }}
                                        </p>
                                      {% endfor %}
                                    </div>

                                <div style="display: grid; grid-template-columns: auto 1fr; gap: 16px;">
                                    <div style="margin-top: 2px;">
                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                             xmlns="http://www.w3.org/2000/svg">
                                            <path d="M10.8333 5.83333C10.8333 6.29357 10.4602 6.66666 9.99999 6.66666C9.53975 6.66666 9.16666 6.29357 9.16666 5.83333C9.16666 5.37309 9.53975 5 9.99999 5C10.4602 5 10.8333 5.37309 10.8333 5.83333Z"
                                                  fill="#667085"/>
                                            <path d="M9.99999 7.5C10.4602 7.5 10.8333 7.87309 10.8333 8.33333V14.1667C10.8333 14.6269 10.4602 15 9.99999 15C9.53975 15 9.16666 14.6269 9.16666 14.1667V8.33333C9.16666 7.87309 9.53975 7.5 9.99999 7.5Z"
                                                  fill="#667085"/>
                                            <path fill-rule="evenodd" clip-rule="evenodd"
                                                  d="M18.3333 10C18.3333 14.6024 14.6024 18.3333 9.99999 18.3333C5.39762 18.3333 1.66666 14.6024 1.66666 10C1.66666 5.39762 5.39762 1.66666 9.99999 1.66666C14.6024 1.66666 18.3333 5.39762 18.3333 10ZM16.6667 10C16.6667 13.6819 13.6819 16.6667 9.99999 16.6667C6.31809 16.6667 3.33332 13.6819 3.33332 10C3.33332 6.3181 6.31809 3.33333 9.99999 3.33333C13.6819 3.33333 16.6667 6.3181 16.6667 10Z"
                                                  fill="#667085"/>
                                        </svg>

                                    </div>

                                    <div>
                                        <div style="margin-bottom: 4px; font-size: 16px; line-height: 24px;">
                                            Address
                                        </div>

                                        <div class="color-secondary">
                                            {{ account.formatted_address }}
                                            <br>
                                            <a
                                                    target="_blank" href="tel:{{contact_phone}}"
                                                    style="text-decoration: underline;"
                                            >
                                                Not available
                                            </a>
                                            <br>
                                            <a
                                                    target="_blank" href="mailto:{{hcp.email}}"
                                                    style="text-decoration: underline;"
                                            >
                                                {{ hcp.email }}
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div style="display: flex; align-items: flex-start">
                            {% for finding in sales.findings %}
                                {% if finding.type == 'cross_selling_opportunities' %}
                                    <div style="margin-right: 14px;">
                                        <table class="round-box round-box--secondary">
                                            <tbody>
                                                <tr>
                                                    <td>
                                                        <svg class="icon" width="24" height="24" viewBox="0 0 24 24"
                                                             fill="none"
                                                             xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M17.0429 5.20711C16.6524 4.81658 16.6524 4.18342 17.0429 3.79289C17.4334 3.40237 18.0666 3.40237 18.4571 3.79289L21.3107 6.64645C21.5059 6.84171 21.5059 7.15829 21.3107 7.35355L18.4571 10.2071C18.0666 10.5976 17.4334 10.5976 17.0429 10.2071C16.6524 9.81658 16.6524 9.18342 17.0429 8.79289L17.8358 8H17.2857C16.7384 8 16.2149 8.22433 15.8374 8.62069L13.9573 10.5948C13.7603 10.8017 13.4302 10.8017 13.2332 10.5948L12.5427 9.86983C12.3588 9.67672 12.3588 9.37328 12.5427 9.18017L14.3892 7.24138C15.1441 6.44866 16.191 6 17.2857 6H17.8358L17.0429 5.20711Z"
                                                                  fill="#002994"/>
                                                            <path d="M17.0429 15.2071C16.6524 14.8166 16.6524 14.1834 17.0429 13.7929C17.4334 13.4024 18.0666 13.4024 18.4571 13.7929L21.3107 16.6464C21.5059 16.8417 21.5059 17.1583 21.3107 17.3536L18.4571 20.2071C18.0666 20.5976 17.4334 20.5976 17.0429 20.2071C16.6524 19.8166 16.6524 19.1834 17.0429 18.7929L17.8358 18H17.2857C16.191 18 15.1441 17.5513 14.3892 16.7586L11.2381 13.45L7.61084 17.2586C6.85587 18.0513 5.80899 18.5 4.71429 18.5H3.5C2.94772 18.5 2.5 18.0523 2.5 17.5C2.5 16.9477 2.94772 16.5 3.5 16.5H4.71429C5.26164 16.5 5.78508 16.2757 6.16256 15.8793L9.85714 12L6.16256 8.12069C5.78508 7.72433 5.26164 7.5 4.71429 7.5H3.5C2.94772 7.5 2.5 7.05229 2.5 6.5C2.5 5.94771 2.94772 5.5 3.5 5.5H4.71429C5.80899 5.5 6.85587 5.94866 7.61084 6.74138L15.8374 15.3793C16.2149 15.7757 16.7384 16 17.2857 16H17.8358L17.0429 15.2071Z"
                                                                  fill="#002994"/>
                                                        </svg>
                                                    </td>
                                                    <td>{{ finding.text }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                {% elif finding.type == 'msd_orders_recommendations' %}
                                    <div style="margin-right: 14px;">
                                        <table class="round-box round-box--secondary">
                                            <tbody>
                                                <tr>
                                                    <td>
                                                        <svg class="icon" width="24" height="24" viewBox="0 0 24 24"
                                                             fill="none"
                                                             xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M17.0429 5.20711C16.6524 4.81658 16.6524 4.18342 17.0429 3.79289C17.4334 3.40237 18.0666 3.40237 18.4571 3.79289L21.3107 6.64645C21.5059 6.84171 21.5059 7.15829 21.3107 7.35355L18.4571 10.2071C18.0666 10.5976 17.4334 10.5976 17.0429 10.2071C16.6524 9.81658 16.6524 9.18342 17.0429 8.79289L17.8358 8H17.2857C16.7384 8 16.2149 8.22433 15.8374 8.62069L13.9573 10.5948C13.7603 10.8017 13.4302 10.8017 13.2332 10.5948L12.5427 9.86983C12.3588 9.67672 12.3588 9.37328 12.5427 9.18017L14.3892 7.24138C15.1441 6.44866 16.191 6 17.2857 6H17.8358L17.0429 5.20711Z"
                                                                  fill="#002994"/>
                                                            <path d="M17.0429 15.2071C16.6524 14.8166 16.6524 14.1834 17.0429 13.7929C17.4334 13.4024 18.0666 13.4024 18.4571 13.7929L21.3107 16.6464C21.5059 16.8417 21.5059 17.1583 21.3107 17.3536L18.4571 20.2071C18.0666 20.5976 17.4334 20.5976 17.0429 20.2071C16.6524 19.8166 16.6524 19.1834 17.0429 18.7929L17.8358 18H17.2857C16.191 18 15.1441 17.5513 14.3892 16.7586L11.2381 13.45L7.61084 17.2586C6.85587 18.0513 5.80899 18.5 4.71429 18.5H3.5C2.94772 18.5 2.5 18.0523 2.5 17.5C2.5 16.9477 2.94772 16.5 3.5 16.5H4.71429C5.26164 16.5 5.78508 16.2757 6.16256 15.8793L9.85714 12L6.16256 8.12069C5.78508 7.72433 5.26164 7.5 4.71429 7.5H3.5C2.94772 7.5 2.5 7.05229 2.5 6.5C2.5 5.94771 2.94772 5.5 3.5 5.5H4.71429C5.80899 5.5 6.85587 5.94866 7.61084 6.74138L15.8374 15.3793C16.2149 15.7757 16.7384 16 17.2857 16H17.8358L17.0429 15.2071Z"
                                                                  fill="#002994"/>
                                                        </svg>
                                                    </td>
                                                    <td>{{ finding.text }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                {% elif finding.type == 'high_performing_account' %}
                                    <div style="margin-right: 14px;">
                                        <table class="round-box round-box--success">
                                            <tbody>
                                                <tr>
                                                    <td>
                                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                             fill="none"
                                                             xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M17.9167 5.83333C18.1468 5.83333 18.3333 6.01988 18.3333 6.24999V9.99999C18.3333 10.4602 17.9602 10.8333 17.5 10.8333C17.0398 10.8333 16.6667 10.4602 16.6667 9.99999V8.67851L12.5505 12.7946C12.0624 13.2828 11.2709 13.2828 10.7828 12.7946L8.33332 10.3452L3.08925 15.5893C2.76381 15.9147 2.23617 15.9147 1.91073 15.5893C1.5853 15.2638 1.5853 14.7362 1.91073 14.4107L7.44944 8.87203C7.9376 8.38388 8.72905 8.38388 9.21721 8.87203L11.6667 11.3215L15.4881 7.49999H14.1667C13.7064 7.49999 13.3333 7.1269 13.3333 6.66666C13.3333 6.20642 13.7064 5.83333 14.1667 5.83333H17.9167Z"
                                                                  fill="#009484"/>
                                                        </svg>
                                                    </td>
                                                    <td>{{ finding.text }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                {% elif finding.type == 'cantonal_program_recommendation' %}
                                    <div style="margin-right: 14px;">
                                        <table class="round-box round-box--success">
                                            <tbody>
                                                <tr>
                                                    <td>
                                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                             fill="none"
                                                             xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M17.9167 5.83333C18.1468 5.83333 18.3333 6.01988 18.3333 6.24999V9.99999C18.3333 10.4602 17.9602 10.8333 17.5 10.8333C17.0398 10.8333 16.6667 10.4602 16.6667 9.99999V8.67851L12.5505 12.7946C12.0624 13.2828 11.2709 13.2828 10.7828 12.7946L8.33332 10.3452L3.08925 15.5893C2.76381 15.9147 2.23617 15.9147 1.91073 15.5893C1.5853 15.2638 1.5853 14.7362 1.91073 14.4107L7.44944 8.87203C7.9376 8.38388 8.72905 8.38388 9.21721 8.87203L11.6667 11.3215L15.4881 7.49999H14.1667C13.7064 7.49999 13.3333 7.1269 13.3333 6.66666C13.3333 6.20642 13.7064 5.83333 14.1667 5.83333H17.9167Z"
                                                                  fill="#009484"/>
                                                        </svg>
                                                    </td>
                                                    <td>{{ finding.text }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                {% endif %}
                            {% endfor %}
                            </div>

                            <div
                                    style="display: grid; gap: 24px; margin-top: 10px"
                            >
                                <div class="card no-split">
                                    <div class="card__table-header-wrapper">
                                        <div class="card__table-header">
                                            <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                 fill="none"
                                                 xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                      d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                                                      fill="#667085"/>
                                            </svg>
                                            <div style="font-size: 18px;">
                                                Account Product Performance
                                            </div>
                                            <div class="round-box round-box--success">
                                                {{ report_month }}
                                            </div>
                                            <a target="_blank" href="{{account.qlik_url}}">
                                                <svg class="icon" width="24" height="24" viewBox="0 0 24 24"
                                                     fill="none" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M15.9497 9.46447V15.5356C15.9497 16.0878 16.3975 16.5356 16.9497 16.5356C17.502 16.5356 17.9497 16.0878 17.9497 15.5356L17.9497 6.55027C17.9497 6.27413 17.7259 6.05027 17.4497 6.05027L16.9545 6.05027C16.9513 6.05026 16.9481 6.05026 16.9449 6.05027L8.46445 6.05027C7.91217 6.05027 7.46445 6.49799 7.46445 7.05027C7.46446 7.60256 7.91217 8.05027 8.46445 8.05027H14.5355L6.34313 16.2427C5.9526 16.6332 5.9526 17.2663 6.34313 17.6569C6.73365 18.0474 7.36681 18.0474 7.75734 17.6569L15.9497 9.46447Z"
                                                          fill="#667085"/>
                                                </svg>
                                            </a>
                                        </div>
                                    </div>
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Moving annual</th>
                                                <th>Rolling quarter</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        {% if sales.metrics|length == 0 %}
                                            <tr>
                                                <td colspan="3">
                                                    No data available
                                                </td>
                                            </tr>
                                        {% endif %}

                                        {% for sale in sales.metrics %}
                                            <tr>
                                                <td>{{ sale.product_name }}</td>

                                                <td class="color-secondary">
                                                    <span>
                                                        {{ sale.mat }} CHF
                                                    </span>

                                                    {% if sale.mat_change > 0 %}
                                                    <span class="badge badge--success">
                                                        {{ sale.mat_change }} %
                                                    </span>
                                                    {% elif sale.mat_change == 0 %}
                                                    <span class="badge badge--neutral">
                                                        {{ sale.mat_change }} %
                                                    </span>
                                                    {% elif sale.mat_change < 0 %}
                                                    <span class="badge badge--danger">
                                                        {{ sale.mat_change }} %
                                                    </span>
                                                    {% endif %}
                                                </td>
                                                <td class="color-secondary">
                                                    <span>
                                                        {{ sale.rolq }} CHF
                                                    </span>
                                                    {% if sale.rolq_change > 0 %}
                                                    <span class="badge badge--success">
                                                        {{ sale.rolq_change }} %
                                                    </span>
                                                    {% elif sale.rolq_change == 0 %}
                                                    <span class="badge badge--neutral">
                                                        {{ sale.rolq_change }} %
                                                    </span>
                                                    {% elif sale.rolq_change < 0 %}
                                                    <span class="badge badge--danger">
                                                        {{ sale.rolq_change }} %
                                                    </span>
                                                    {% endif %}
                                                </td>
                                            </tr>
                                        {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                                {% if sales.trends|length > 0 %}
                                <div style="display: flex;">
                                    <div style="margin: 2px 16px 0 0;">
                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                             xmlns="http://www.w3.org/2000/svg">
                                            <g clip-path="url(#clip0_48_503)">
                                                <path d="M11.3185 1.45181C11.6723 2.02472 11.9146 3.44562 12.0418 5.32713H14.3024V3.33006C14.2536 3.3089 14.2065 3.28449 14.1612 3.25682C14.0758 3.20636 13.9974 3.14777 13.9294 3.08429L13.9207 3.07615C13.8004 2.96385 13.7046 2.82876 13.6383 2.67902C13.5721 2.53091 13.5355 2.36815 13.5355 2.19725C13.5355 2.02798 13.5721 1.86684 13.6383 1.7171C13.7063 1.56248 13.8074 1.42414 13.9294 1.30858C14.0532 1.19302 14.2013 1.10024 14.3669 1.03677C14.5255 0.974917 14.6998 0.940737 14.881 0.940737C15.0623 0.940737 15.2349 0.974917 15.3952 1.03677C15.5608 1.10024 15.7089 1.19464 15.8327 1.30858C15.9564 1.42414 16.0558 1.56248 16.1238 1.71548L16.1272 1.72524C16.19 1.87173 16.2248 2.03123 16.2248 2.19562C16.2248 2.36489 16.1882 2.52602 16.122 2.67576C16.054 2.83039 15.9529 2.96873 15.8309 3.08429L15.8205 3.09406C15.7595 3.1494 15.6915 3.20148 15.62 3.24543C15.5817 3.26984 15.5416 3.291 15.4998 3.31216V5.89028C15.4998 6.0449 15.4318 6.18488 15.3238 6.28579C15.2157 6.3867 15.0658 6.45018 14.9002 6.45018H12.1011C12.122 6.98566 12.136 7.54881 12.1412 8.12987H17.4466C17.4693 8.08755 17.4937 8.04686 17.5198 8.0078L17.5268 7.99966C17.5773 7.92642 17.6366 7.85968 17.6994 7.80109C17.8231 7.68553 17.9712 7.59276 18.1368 7.52928L18.1473 7.52602C18.3041 7.46743 18.4749 7.43325 18.651 7.43325C18.8322 7.43325 19.0048 7.46743 19.1651 7.52928C19.3307 7.59276 19.4789 7.68716 19.6026 7.80109C19.7264 7.91665 19.8257 8.055 19.8937 8.20962C19.9599 8.35936 19.9965 8.52049 19.9965 8.68976C19.9965 8.85903 19.9599 9.02017 19.8937 9.1699C19.8257 9.32453 19.7246 9.46287 19.6026 9.57843C19.4789 9.69399 19.3307 9.78677 19.1651 9.85024L19.1547 9.8535C18.9978 9.91209 18.827 9.94464 18.651 9.94464C18.4697 9.94464 18.2954 9.91046 18.1368 9.84862C17.973 9.78514 17.8248 9.69237 17.6994 9.57681C17.6331 9.51496 17.5739 9.4466 17.5216 9.3701C17.4937 9.33104 17.4693 9.29035 17.4466 9.24803H12.1429C12.1377 9.8828 12.1238 10.5322 12.1011 11.193H18.5865C18.7521 11.193 18.902 11.2565 19.01 11.3574C19.1181 11.4583 19.1861 11.5983 19.1861 11.7529V15.9082C19.2436 15.931 19.2976 15.957 19.3499 15.9863C19.444 16.0384 19.5294 16.1019 19.6061 16.1735C19.7299 16.289 19.8292 16.4274 19.8972 16.582L19.9007 16.5918C19.9634 16.7383 20 16.8978 20 17.0622C20 17.2314 19.9634 17.3926 19.8972 17.5423C19.8292 17.6969 19.7281 17.8353 19.6061 17.9508C19.4824 18.0664 19.3342 18.1592 19.1686 18.2226C19.01 18.2845 18.8357 18.3187 18.6545 18.3187C18.4732 18.3187 18.3007 18.2845 18.1403 18.2226C17.9747 18.1592 17.8266 18.0648 17.7028 17.9508C17.5791 17.8353 17.4797 17.6969 17.4118 17.5423C17.3455 17.3942 17.3089 17.2314 17.3089 17.0622C17.3089 16.8929 17.3455 16.7301 17.4118 16.582C17.4797 16.4274 17.5808 16.289 17.7028 16.1735C17.7586 16.1214 17.8214 16.0726 17.8876 16.0286C17.919 16.0075 17.9521 15.9879 17.9869 15.97V12.3144H12.054C12.0279 12.8418 11.9965 13.3708 11.9582 13.8981H13.8824C14.0479 13.8981 14.1978 13.9616 14.3059 14.0625C14.4139 14.1634 14.4819 14.3034 14.4819 14.458V16.6813C14.5255 16.7025 14.5656 16.7252 14.6074 16.7497C14.6876 16.7985 14.759 16.8538 14.8235 16.914L14.834 16.9238C14.9525 17.0377 15.0501 17.1728 15.1163 17.3226C15.1826 17.4707 15.2192 17.6334 15.2192 17.8027C15.2192 17.972 15.1826 18.1347 15.1163 18.2829L15.1111 18.2926C15.0431 18.444 14.9438 18.5791 14.8235 18.6914L14.8148 18.6995C14.6928 18.8118 14.5482 18.903 14.3895 18.9648C14.2309 19.0267 14.0549 19.0609 13.8736 19.0609C13.6924 19.0609 13.5198 19.0267 13.3595 18.9648C13.1939 18.9014 13.0458 18.8069 12.922 18.693L12.9116 18.6833C12.793 18.5693 12.6954 18.4342 12.6292 18.2845C12.563 18.1347 12.5264 17.9736 12.5264 17.8043C12.5264 17.6351 12.563 17.4739 12.6292 17.3242C12.6972 17.1696 12.7965 17.0312 12.9203 16.9157C12.9882 16.8522 13.0649 16.7952 13.1451 16.7464C13.1887 16.7204 13.234 16.6959 13.281 16.6748V15.0195H11.8693C11.8501 15.2425 11.8292 15.4655 11.8083 15.6868C11.7804 15.9733 11.6915 16.5023 11.749 16.7643C11.9024 17.4593 11.2314 19.5556 9.25839 19.9414C8.28584 20.1302 7.28018 19.8519 6.52201 19.2985C5.91547 18.8574 5.46057 18.2373 5.29674 17.5358C4.97952 17.5244 4.65708 17.4642 4.34336 17.3665C3.64968 17.1484 2.98214 16.7236 2.46101 16.1605C1.93639 15.5957 1.55643 14.8861 1.43617 14.0967C1.37517 13.6849 1.38388 13.2552 1.48149 12.8125C1.14162 12.5244 0.848805 12.2005 0.616997 11.8473C0.21264 11.2435 -0.00871084 10.5631 3.75378e-06 9.86326C0.00871835 9.15851 0.249241 8.44399 0.770374 7.77993C1.07364 7.39419 1.47277 7.02635 1.97822 6.68944C1.97299 6.56085 1.97299 6.43227 1.97647 6.30532C2.01656 5.27668 2.42266 4.37173 3.01525 3.69627C3.62876 2.9964 4.44968 2.53904 5.29325 2.42674H5.29674C5.32637 2.31118 5.36122 2.19725 5.40654 2.08657C5.67844 1.39809 6.23791 0.812157 6.92288 0.439435C7.61308 0.0650865 8.44096 -0.100929 9.24793 0.0553208C10.0235 0.208316 10.7625 0.641258 11.3185 1.45181ZM5.36297 16.1474C5.64881 15.3076 6.40349 14.4694 7.82745 13.7907C8.18301 13.623 8.61525 13.7532 8.79826 14.0836C8.97778 14.4157 8.83835 14.8193 8.48454 14.9902C7.16515 15.6201 6.66841 16.3428 6.66841 16.9726C6.66841 17.4642 6.9682 17.9232 7.40393 18.2422C7.84663 18.5628 8.4183 18.7305 8.95861 18.6263C9.63138 18.4961 10.2797 17.915 10.6161 16.6487V3.33494C10.2797 2.07843 9.63138 1.50063 8.96035 1.37042C8.51765 1.28416 8.04706 1.38182 7.64619 1.60154C7.24009 1.82127 6.91417 2.15981 6.75905 2.55044C6.55338 3.07127 6.67538 3.71092 7.37255 4.31313C7.66188 4.56541 7.68105 4.98696 7.4109 5.25714C7.14074 5.52733 6.68933 5.54523 6.4 5.29295C5.85796 4.8242 5.52332 4.32615 5.356 3.82974C4.92898 3.92576 4.50719 4.18944 4.16558 4.57681C3.76645 5.03091 3.49281 5.64614 3.46493 6.35252C3.45796 6.5397 3.46841 6.73826 3.49804 6.94171H3.4963C3.53464 7.20539 3.40915 7.47882 3.1512 7.62694C2.62833 7.92641 2.24314 8.25682 1.97299 8.60024C1.64532 9.01691 1.49543 9.45474 1.4902 9.87628C1.48497 10.3043 1.62615 10.7308 1.87887 11.1133C2.09325 11.4372 2.38606 11.7334 2.74336 11.9808C3.01177 12.1533 3.13726 12.4756 3.02746 12.7767C2.88628 13.1673 2.85491 13.5465 2.90894 13.8997C2.98562 14.4075 3.23835 14.8714 3.58345 15.2441C3.93029 15.6185 4.3695 15.8984 4.81918 16.0416C5.00044 16.1068 5.18345 16.1393 5.36297 16.1474ZM5.5268 6.68944C5.80915 6.43065 6.26231 6.4339 6.54118 6.69757C6.8183 6.96125 6.81482 7.38442 6.53247 7.64484C5.91721 8.21125 5.59652 8.94041 5.56166 9.68585C5.52854 10.4541 5.79521 11.2451 6.35643 11.8945C6.60567 12.1826 6.55512 12.6041 6.24663 12.8369C5.93813 13.0696 5.48671 13.0224 5.23748 12.7344C4.45142 11.8245 4.07844 10.7178 4.12549 9.63214C4.17604 8.55467 4.63966 7.50324 5.5268 6.68944Z"
                                                      fill="#667085"/>
                                            </g>
                                            <defs>
                                                <clipPath id="clip0_48_503">
                                                    <rect width="20" height="20" fill="white"/>
                                                </clipPath>
                                            </defs>
                                        </svg>

                                    </div>

                                    <div>
                                        <div style="margin-bottom: 4px; font-size: 16px; line-height: 24px;">
                                            Trends
                                        </div>
                                        <div class="color-secondary">
                                            <ul>
                                                {% for trend in sales.trends %}
                                                <li>
                                                    {{ trend.text }}
                                                </li>
                                                {% endfor %}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                {% endif %}
                                <div class="card no-split">
                                    <div class="card__table-header-wrapper">
                                        <div class="card__table-header">
                                            <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                 fill="none"
                                                 xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                      d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                                                      fill="#667085"/>
                                            </svg>
                                            <div style="font-size: 18px;">
                                                Engagement table
                                            </div>
                                            <div class="round-box round-box--success">
                                                {{ report_month }}
                                            </div>
                                            <a target="_blank" href="{{account.qlik_url}}">
                                                <svg class="icon" width="24" height="24" viewBox="0 0 24 24"
                                                     fill="none" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M15.9497 9.46447V15.5356C15.9497 16.0878 16.3975 16.5356 16.9497 16.5356C17.502 16.5356 17.9497 16.0878 17.9497 15.5356L17.9497 6.55027C17.9497 6.27413 17.7259 6.05027 17.4497 6.05027L16.9545 6.05027C16.9513 6.05026 16.9481 6.05026 16.9449 6.05027L8.46445 6.05027C7.91217 6.05027 7.46445 6.49799 7.46445 7.05027C7.46446 7.60256 7.91217 8.05027 8.46445 8.05027H14.5355L6.34313 16.2427C5.9526 16.6332 5.9526 17.2663 6.34313 17.6569C6.73365 18.0474 7.36681 18.0474 7.75734 17.6569L15.9497 9.46447Z"
                                                          fill="#667085"/>
                                                </svg>
                                            </a>
                                        </div>
                                    </div>
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Channel</th>
                                                <th>Moving annual</th>
                                                <th>Rolling quarter</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% if interactions.metrics|length == 0 %}
                                                <tr>
                                                    <td colspan="3">
                                                        No data available
                                                    </td>
                                                </tr>
                                            {% endif %}
                                            {% for interaction in interactions.metrics %}
                                            <tr>
                                                <td>{{ interaction.channel }}</td>

                                                <td class="color-secondary">
                                                    <span>{{ interaction.mat }}</span>
                                                    {% if interaction.mat_change > 0 %}
                                                    <span class="badge badge--success">
                                                        {{ interaction.mat_change }} %
                                                    </span>
                                                    {% elif interaction.mat_change == 0 %}
                                                    <span class="badge badge--neutral">
                                                        {{ interaction.mat_change }} %
                                                    </span>
                                                    {% elif interaction.mat_change < 0 %}
                                                    <span class="badge badge--danger">
                                                        {{ interaction.mat_change }} %
                                                    </span>
                                                    {% endif %}

                                                </td>
                                                <td class="color-secondary">
                                                    <span>{{ interaction.rolq }}</span>
                                                    {% if interaction.rolq_change > 0 %}
                                                    <span class="badge badge--success">
                                                        {{ interaction.rolq_change }} %
                                                    </span>
                                                    {% elif interaction.rolq_change == 0 %}
                                                    <span class="badge badge--neutral">
                                                        {{ interaction.rolq_change }} %
                                                    </span>
                                                    {% elif interaction.rolq_change < 0 %}
                                                    <span class="badge badge--danger">
                                                        {{ interaction.rolq_change }} %
                                                    </span>
                                                    {% endif %}
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                                {% if sales.insights|length > 0 %}
                                <div style="display: flex;">
                                    <div style="margin: 2px 16px 0 0;">
                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                             xmlns="http://www.w3.org/2000/svg">
                                            <g clip-path="url(#clip0_48_503)">
                                                <path d="M11.3185 1.45181C11.6723 2.02472 11.9146 3.44562 12.0418 5.32713H14.3024V3.33006C14.2536 3.3089 14.2065 3.28449 14.1612 3.25682C14.0758 3.20636 13.9974 3.14777 13.9294 3.08429L13.9207 3.07615C13.8004 2.96385 13.7046 2.82876 13.6383 2.67902C13.5721 2.53091 13.5355 2.36815 13.5355 2.19725C13.5355 2.02798 13.5721 1.86684 13.6383 1.7171C13.7063 1.56248 13.8074 1.42414 13.9294 1.30858C14.0532 1.19302 14.2013 1.10024 14.3669 1.03677C14.5255 0.974917 14.6998 0.940737 14.881 0.940737C15.0623 0.940737 15.2349 0.974917 15.3952 1.03677C15.5608 1.10024 15.7089 1.19464 15.8327 1.30858C15.9564 1.42414 16.0558 1.56248 16.1238 1.71548L16.1272 1.72524C16.19 1.87173 16.2248 2.03123 16.2248 2.19562C16.2248 2.36489 16.1882 2.52602 16.122 2.67576C16.054 2.83039 15.9529 2.96873 15.8309 3.08429L15.8205 3.09406C15.7595 3.1494 15.6915 3.20148 15.62 3.24543C15.5817 3.26984 15.5416 3.291 15.4998 3.31216V5.89028C15.4998 6.0449 15.4318 6.18488 15.3238 6.28579C15.2157 6.3867 15.0658 6.45018 14.9002 6.45018H12.1011C12.122 6.98566 12.136 7.54881 12.1412 8.12987H17.4466C17.4693 8.08755 17.4937 8.04686 17.5198 8.0078L17.5268 7.99966C17.5773 7.92642 17.6366 7.85968 17.6994 7.80109C17.8231 7.68553 17.9712 7.59276 18.1368 7.52928L18.1473 7.52602C18.3041 7.46743 18.4749 7.43325 18.651 7.43325C18.8322 7.43325 19.0048 7.46743 19.1651 7.52928C19.3307 7.59276 19.4789 7.68716 19.6026 7.80109C19.7264 7.91665 19.8257 8.055 19.8937 8.20962C19.9599 8.35936 19.9965 8.52049 19.9965 8.68976C19.9965 8.85903 19.9599 9.02017 19.8937 9.1699C19.8257 9.32453 19.7246 9.46287 19.6026 9.57843C19.4789 9.69399 19.3307 9.78677 19.1651 9.85024L19.1547 9.8535C18.9978 9.91209 18.827 9.94464 18.651 9.94464C18.4697 9.94464 18.2954 9.91046 18.1368 9.84862C17.973 9.78514 17.8248 9.69237 17.6994 9.57681C17.6331 9.51496 17.5739 9.4466 17.5216 9.3701C17.4937 9.33104 17.4693 9.29035 17.4466 9.24803H12.1429C12.1377 9.8828 12.1238 10.5322 12.1011 11.193H18.5865C18.7521 11.193 18.902 11.2565 19.01 11.3574C19.1181 11.4583 19.1861 11.5983 19.1861 11.7529V15.9082C19.2436 15.931 19.2976 15.957 19.3499 15.9863C19.444 16.0384 19.5294 16.1019 19.6061 16.1735C19.7299 16.289 19.8292 16.4274 19.8972 16.582L19.9007 16.5918C19.9634 16.7383 20 16.8978 20 17.0622C20 17.2314 19.9634 17.3926 19.8972 17.5423C19.8292 17.6969 19.7281 17.8353 19.6061 17.9508C19.4824 18.0664 19.3342 18.1592 19.1686 18.2226C19.01 18.2845 18.8357 18.3187 18.6545 18.3187C18.4732 18.3187 18.3007 18.2845 18.1403 18.2226C17.9747 18.1592 17.8266 18.0648 17.7028 17.9508C17.5791 17.8353 17.4797 17.6969 17.4118 17.5423C17.3455 17.3942 17.3089 17.2314 17.3089 17.0622C17.3089 16.8929 17.3455 16.7301 17.4118 16.582C17.4797 16.4274 17.5808 16.289 17.7028 16.1735C17.7586 16.1214 17.8214 16.0726 17.8876 16.0286C17.919 16.0075 17.9521 15.9879 17.9869 15.97V12.3144H12.054C12.0279 12.8418 11.9965 13.3708 11.9582 13.8981H13.8824C14.0479 13.8981 14.1978 13.9616 14.3059 14.0625C14.4139 14.1634 14.4819 14.3034 14.4819 14.458V16.6813C14.5255 16.7025 14.5656 16.7252 14.6074 16.7497C14.6876 16.7985 14.759 16.8538 14.8235 16.914L14.834 16.9238C14.9525 17.0377 15.0501 17.1728 15.1163 17.3226C15.1826 17.4707 15.2192 17.6334 15.2192 17.8027C15.2192 17.972 15.1826 18.1347 15.1163 18.2829L15.1111 18.2926C15.0431 18.444 14.9438 18.5791 14.8235 18.6914L14.8148 18.6995C14.6928 18.8118 14.5482 18.903 14.3895 18.9648C14.2309 19.0267 14.0549 19.0609 13.8736 19.0609C13.6924 19.0609 13.5198 19.0267 13.3595 18.9648C13.1939 18.9014 13.0458 18.8069 12.922 18.693L12.9116 18.6833C12.793 18.5693 12.6954 18.4342 12.6292 18.2845C12.563 18.1347 12.5264 17.9736 12.5264 17.8043C12.5264 17.6351 12.563 17.4739 12.6292 17.3242C12.6972 17.1696 12.7965 17.0312 12.9203 16.9157C12.9882 16.8522 13.0649 16.7952 13.1451 16.7464C13.1887 16.7204 13.234 16.6959 13.281 16.6748V15.0195H11.8693C11.8501 15.2425 11.8292 15.4655 11.8083 15.6868C11.7804 15.9733 11.6915 16.5023 11.749 16.7643C11.9024 17.4593 11.2314 19.5556 9.25839 19.9414C8.28584 20.1302 7.28018 19.8519 6.52201 19.2985C5.91547 18.8574 5.46057 18.2373 5.29674 17.5358C4.97952 17.5244 4.65708 17.4642 4.34336 17.3665C3.64968 17.1484 2.98214 16.7236 2.46101 16.1605C1.93639 15.5957 1.55643 14.8861 1.43617 14.0967C1.37517 13.6849 1.38388 13.2552 1.48149 12.8125C1.14162 12.5244 0.848805 12.2005 0.616997 11.8473C0.21264 11.2435 -0.00871084 10.5631 3.75378e-06 9.86326C0.00871835 9.15851 0.249241 8.44399 0.770374 7.77993C1.07364 7.39419 1.47277 7.02635 1.97822 6.68944C1.97299 6.56085 1.97299 6.43227 1.97647 6.30532C2.01656 5.27668 2.42266 4.37173 3.01525 3.69627C3.62876 2.9964 4.44968 2.53904 5.29325 2.42674H5.29674C5.32637 2.31118 5.36122 2.19725 5.40654 2.08657C5.67844 1.39809 6.23791 0.812157 6.92288 0.439435C7.61308 0.0650865 8.44096 -0.100929 9.24793 0.0553208C10.0235 0.208316 10.7625 0.641258 11.3185 1.45181ZM5.36297 16.1474C5.64881 15.3076 6.40349 14.4694 7.82745 13.7907C8.18301 13.623 8.61525 13.7532 8.79826 14.0836C8.97778 14.4157 8.83835 14.8193 8.48454 14.9902C7.16515 15.6201 6.66841 16.3428 6.66841 16.9726C6.66841 17.4642 6.9682 17.9232 7.40393 18.2422C7.84663 18.5628 8.4183 18.7305 8.95861 18.6263C9.63138 18.4961 10.2797 17.915 10.6161 16.6487V3.33494C10.2797 2.07843 9.63138 1.50063 8.96035 1.37042C8.51765 1.28416 8.04706 1.38182 7.64619 1.60154C7.24009 1.82127 6.91417 2.15981 6.75905 2.55044C6.55338 3.07127 6.67538 3.71092 7.37255 4.31313C7.66188 4.56541 7.68105 4.98696 7.4109 5.25714C7.14074 5.52733 6.68933 5.54523 6.4 5.29295C5.85796 4.8242 5.52332 4.32615 5.356 3.82974C4.92898 3.92576 4.50719 4.18944 4.16558 4.57681C3.76645 5.03091 3.49281 5.64614 3.46493 6.35252C3.45796 6.5397 3.46841 6.73826 3.49804 6.94171H3.4963C3.53464 7.20539 3.40915 7.47882 3.1512 7.62694C2.62833 7.92641 2.24314 8.25682 1.97299 8.60024C1.64532 9.01691 1.49543 9.45474 1.4902 9.87628C1.48497 10.3043 1.62615 10.7308 1.87887 11.1133C2.09325 11.4372 2.38606 11.7334 2.74336 11.9808C3.01177 12.1533 3.13726 12.4756 3.02746 12.7767C2.88628 13.1673 2.85491 13.5465 2.90894 13.8997C2.98562 14.4075 3.23835 14.8714 3.58345 15.2441C3.93029 15.6185 4.3695 15.8984 4.81918 16.0416C5.00044 16.1068 5.18345 16.1393 5.36297 16.1474ZM5.5268 6.68944C5.80915 6.43065 6.26231 6.4339 6.54118 6.69757C6.8183 6.96125 6.81482 7.38442 6.53247 7.64484C5.91721 8.21125 5.59652 8.94041 5.56166 9.68585C5.52854 10.4541 5.79521 11.2451 6.35643 11.8945C6.60567 12.1826 6.55512 12.6041 6.24663 12.8369C5.93813 13.0696 5.48671 13.0224 5.23748 12.7344C4.45142 11.8245 4.07844 10.7178 4.12549 9.63214C4.17604 8.55467 4.63966 7.50324 5.5268 6.68944Z"
                                                      fill="#667085"/>
                                            </g>
                                            <defs>
                                                <clipPath id="clip0_48_503">
                                                    <rect width="20" height="20" fill="white"/>
                                                </clipPath>
                                            </defs>
                                        </svg>

                                    </div>
                                    <div>
                                        <div style="margin-bottom: 4px; font-size: 16px; line-height: 24px;">
                                            Sales insights
                                        </div>
                                        {% for insight in sales.insights %}
                                        <p class="color-secondary">
                                            {{ insight.text }}
                                        </p>
                                        {% endfor %}
                                    </div>
                                </div>
                                {% else %}
                                <div style="display: flex;">
                                    <div style="margin: 2px 16px 0 0;">
                                        <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                             xmlns="http://www.w3.org/2000/svg">
                                            <g clip-path="url(#clip0_48_503)">
                                                <path d="M11.3185 1.45181C11.6723 2.02472 11.9146 3.44562 12.0418 5.32713H14.3024V3.33006C14.2536 3.3089 14.2065 3.28449 14.1612 3.25682C14.0758 3.20636 13.9974 3.14777 13.9294 3.08429L13.9207 3.07615C13.8004 2.96385 13.7046 2.82876 13.6383 2.67902C13.5721 2.53091 13.5355 2.36815 13.5355 2.19725C13.5355 2.02798 13.5721 1.86684 13.6383 1.7171C13.7063 1.56248 13.8074 1.42414 13.9294 1.30858C14.0532 1.19302 14.2013 1.10024 14.3669 1.03677C14.5255 0.974917 14.6998 0.940737 14.881 0.940737C15.0623 0.940737 15.2349 0.974917 15.3952 1.03677C15.5608 1.10024 15.7089 1.19464 15.8327 1.30858C15.9564 1.42414 16.0558 1.56248 16.1238 1.71548L16.1272 1.72524C16.19 1.87173 16.2248 2.03123 16.2248 2.19562C16.2248 2.36489 16.1882 2.52602 16.122 2.67576C16.054 2.83039 15.9529 2.96873 15.8309 3.08429L15.8205 3.09406C15.7595 3.1494 15.6915 3.20148 15.62 3.24543C15.5817 3.26984 15.5416 3.291 15.4998 3.31216V5.89028C15.4998 6.0449 15.4318 6.18488 15.3238 6.28579C15.2157 6.3867 15.0658 6.45018 14.9002 6.45018H12.1011C12.122 6.98566 12.136 7.54881 12.1412 8.12987H17.4466C17.4693 8.08755 17.4937 8.04686 17.5198 8.0078L17.5268 7.99966C17.5773 7.92642 17.6366 7.85968 17.6994 7.80109C17.8231 7.68553 17.9712 7.59276 18.1368 7.52928L18.1473 7.52602C18.3041 7.46743 18.4749 7.43325 18.651 7.43325C18.8322 7.43325 19.0048 7.46743 19.1651 7.52928C19.3307 7.59276 19.4789 7.68716 19.6026 7.80109C19.7264 7.91665 19.8257 8.055 19.8937 8.20962C19.9599 8.35936 19.9965 8.52049 19.9965 8.68976C19.9965 8.85903 19.9599 9.02017 19.8937 9.1699C19.8257 9.32453 19.7246 9.46287 19.6026 9.57843C19.4789 9.69399 19.3307 9.78677 19.1651 9.85024L19.1547 9.8535C18.9978 9.91209 18.827 9.94464 18.651 9.94464C18.4697 9.94464 18.2954 9.91046 18.1368 9.84862C17.973 9.78514 17.8248 9.69237 17.6994 9.57681C17.6331 9.51496 17.5739 9.4466 17.5216 9.3701C17.4937 9.33104 17.4693 9.29035 17.4466 9.24803H12.1429C12.1377 9.8828 12.1238 10.5322 12.1011 11.193H18.5865C18.7521 11.193 18.902 11.2565 19.01 11.3574C19.1181 11.4583 19.1861 11.5983 19.1861 11.7529V15.9082C19.2436 15.931 19.2976 15.957 19.3499 15.9863C19.444 16.0384 19.5294 16.1019 19.6061 16.1735C19.7299 16.289 19.8292 16.4274 19.8972 16.582L19.9007 16.5918C19.9634 16.7383 20 16.8978 20 17.0622C20 17.2314 19.9634 17.3926 19.8972 17.5423C19.8292 17.6969 19.7281 17.8353 19.6061 17.9508C19.4824 18.0664 19.3342 18.1592 19.1686 18.2226C19.01 18.2845 18.8357 18.3187 18.6545 18.3187C18.4732 18.3187 18.3007 18.2845 18.1403 18.2226C17.9747 18.1592 17.8266 18.0648 17.7028 17.9508C17.5791 17.8353 17.4797 17.6969 17.4118 17.5423C17.3455 17.3942 17.3089 17.2314 17.3089 17.0622C17.3089 16.8929 17.3455 16.7301 17.4118 16.582C17.4797 16.4274 17.5808 16.289 17.7028 16.1735C17.7586 16.1214 17.8214 16.0726 17.8876 16.0286C17.919 16.0075 17.9521 15.9879 17.9869 15.97V12.3144H12.054C12.0279 12.8418 11.9965 13.3708 11.9582 13.8981H13.8824C14.0479 13.8981 14.1978 13.9616 14.3059 14.0625C14.4139 14.1634 14.4819 14.3034 14.4819 14.458V16.6813C14.5255 16.7025 14.5656 16.7252 14.6074 16.7497C14.6876 16.7985 14.759 16.8538 14.8235 16.914L14.834 16.9238C14.9525 17.0377 15.0501 17.1728 15.1163 17.3226C15.1826 17.4707 15.2192 17.6334 15.2192 17.8027C15.2192 17.972 15.1826 18.1347 15.1163 18.2829L15.1111 18.2926C15.0431 18.444 14.9438 18.5791 14.8235 18.6914L14.8148 18.6995C14.6928 18.8118 14.5482 18.903 14.3895 18.9648C14.2309 19.0267 14.0549 19.0609 13.8736 19.0609C13.6924 19.0609 13.5198 19.0267 13.3595 18.9648C13.1939 18.9014 13.0458 18.8069 12.922 18.693L12.9116 18.6833C12.793 18.5693 12.6954 18.4342 12.6292 18.2845C12.563 18.1347 12.5264 17.9736 12.5264 17.8043C12.5264 17.6351 12.563 17.4739 12.6292 17.3242C12.6972 17.1696 12.7965 17.0312 12.9203 16.9157C12.9882 16.8522 13.0649 16.7952 13.1451 16.7464C13.1887 16.7204 13.234 16.6959 13.281 16.6748V15.0195H11.8693C11.8501 15.2425 11.8292 15.4655 11.8083 15.6868C11.7804 15.9733 11.6915 16.5023 11.749 16.7643C11.9024 17.4593 11.2314 19.5556 9.25839 19.9414C8.28584 20.1302 7.28018 19.8519 6.52201 19.2985C5.91547 18.8574 5.46057 18.2373 5.29674 17.5358C4.97952 17.5244 4.65708 17.4642 4.34336 17.3665C3.64968 17.1484 2.98214 16.7236 2.46101 16.1605C1.93639 15.5957 1.55643 14.8861 1.43617 14.0967C1.37517 13.6849 1.38388 13.2552 1.48149 12.8125C1.14162 12.5244 0.848805 12.2005 0.616997 11.8473C0.21264 11.2435 -0.00871084 10.5631 3.75378e-06 9.86326C0.00871835 9.15851 0.249241 8.44399 0.770374 7.77993C1.07364 7.39419 1.47277 7.02635 1.97822 6.68944C1.97299 6.56085 1.97299 6.43227 1.97647 6.30532C2.01656 5.27668 2.42266 4.37173 3.01525 3.69627C3.62876 2.9964 4.44968 2.53904 5.29325 2.42674H5.29674C5.32637 2.31118 5.36122 2.19725 5.40654 2.08657C5.67844 1.39809 6.23791 0.812157 6.92288 0.439435C7.61308 0.0650865 8.44096 -0.100929 9.24793 0.0553208C10.0235 0.208316 10.7625 0.641258 11.3185 1.45181ZM5.36297 16.1474C5.64881 15.3076 6.40349 14.4694 7.82745 13.7907C8.18301 13.623 8.61525 13.7532 8.79826 14.0836C8.97778 14.4157 8.83835 14.8193 8.48454 14.9902C7.16515 15.6201 6.66841 16.3428 6.66841 16.9726C6.66841 17.4642 6.9682 17.9232 7.40393 18.2422C7.84663 18.5628 8.4183 18.7305 8.95861 18.6263C9.63138 18.4961 10.2797 17.915 10.6161 16.6487V3.33494C10.2797 2.07843 9.63138 1.50063 8.96035 1.37042C8.51765 1.28416 8.04706 1.38182 7.64619 1.60154C7.24009 1.82127 6.91417 2.15981 6.75905 2.55044C6.55338 3.07127 6.67538 3.71092 7.37255 4.31313C7.66188 4.56541 7.68105 4.98696 7.4109 5.25714C7.14074 5.52733 6.68933 5.54523 6.4 5.29295C5.85796 4.8242 5.52332 4.32615 5.356 3.82974C4.92898 3.92576 4.50719 4.18944 4.16558 4.57681C3.76645 5.03091 3.49281 5.64614 3.46493 6.35252C3.45796 6.5397 3.46841 6.73826 3.49804 6.94171H3.4963C3.53464 7.20539 3.40915 7.47882 3.1512 7.62694C2.62833 7.92641 2.24314 8.25682 1.97299 8.60024C1.64532 9.01691 1.49543 9.45474 1.4902 9.87628C1.48497 10.3043 1.62615 10.7308 1.87887 11.1133C2.09325 11.4372 2.38606 11.7334 2.74336 11.9808C3.01177 12.1533 3.13726 12.4756 3.02746 12.7767C2.88628 13.1673 2.85491 13.5465 2.90894 13.8997C2.98562 14.4075 3.23835 14.8714 3.58345 15.2441C3.93029 15.6185 4.3695 15.8984 4.81918 16.0416C5.00044 16.1068 5.18345 16.1393 5.36297 16.1474ZM5.5268 6.68944C5.80915 6.43065 6.26231 6.4339 6.54118 6.69757C6.8183 6.96125 6.81482 7.38442 6.53247 7.64484C5.91721 8.21125 5.59652 8.94041 5.56166 9.68585C5.52854 10.4541 5.79521 11.2451 6.35643 11.8945C6.60567 12.1826 6.55512 12.6041 6.24663 12.8369C5.93813 13.0696 5.48671 13.0224 5.23748 12.7344C4.45142 11.8245 4.07844 10.7178 4.12549 9.63214C4.17604 8.55467 4.63966 7.50324 5.5268 6.68944Z"
                                                      fill="#667085"/>
                                            </g>
                                            <defs>
                                                <clipPath id="clip0_48_503">
                                                    <rect width="20" height="20" fill="white"/>
                                                </clipPath>
                                            </defs>
                                        </svg>

                                    </div>
                                    <div>
                                        <div style="margin-bottom: 4px; font-size: 16px; line-height: 24px;">
                                            Sales Insights
                                        </div>
                                        <p class="color-secondary">
                                            Insights not available
                                        </p>
                                    </div>
                                </div>
                                {% endif %}
{% if interactions.email_summaries|length > 0 %}
    <div class="card no-split">
        <div class="card__table-header-wrapper">
            <div class="card__table-header">
                <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd"
                          d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                          fill="#667085"/>
                </svg>
                <div style="font-size: 18px;">
                    Email Engagement Insights (AE / ME)
                </div>
            </div>
        </div>
        <div class="card-inner">
            {% for email_summary in interactions.email_summaries %}
                <p class="color-secondary"><strong>{{ email_summary.type }}</strong>{{ email_summary.text }}</p>
            {% endfor %}
            
            <p class="color-secondary"><strong>Unread AE Emails Count: </strong>{{ interactions.email_counts.approved.unread }} / {{ interactions.email_counts.approved.total }}</p>
            <p class="color-secondary"><strong>Read AE Emails Count: </strong>{{ interactions.email_counts.approved.read }} / {{ interactions.email_counts.approved.total }}</p>
            <p class="color-secondary"><strong>Clicked AE Emails Count: </strong>{{ interactions.email_counts.approved.clicked }} / {{ interactions.email_counts.approved.total }}</p>
            <p class="color-secondary"><strong>Unread ME Emails Count: </strong>{{ interactions.email_counts.marketing.unread }} / {{ interactions.email_counts.marketing.total }}</p>
            <p class="color-secondary"><strong>Read ME Emails Count: </strong>{{ interactions.email_counts.marketing.read }} / {{ interactions.email_counts.marketing.total }}</p>
            <p class="color-secondary"><strong>Clicked ME Emails Count: </strong>{{ interactions.email_counts.marketing.clicked }} / {{ interactions.email_counts.marketing.total }}</p>
            <p class="color-secondary"><strong>Bounced AE Emails Count: </strong>{{ interactions.email_counts.approved.bounced }} / {{ interactions.email_counts.approved.total }}</p>
            <p class="color-secondary"><strong>Bounced ME Emails Count: </strong>{{ interactions.email_counts.marketing.bounced }} / {{ interactions.email_counts.marketing.total }}</p>
            {% for bounced_email in interactions.bounced_emails %}
                <p class="color-secondary"><strong>Email</strong>{{ bounced_email.email }} <strong>Subject</strong>{{ bounced_email.subject }} <strong>Date</strong> {{ bounced_email.date }}</p>
            {% endfor %}
         </div> 
    </div>
{% endif %}                                                
                                <div class="card no-split">
                                    <div class="card__table-header-wrapper">
                                        <div class="card__table-header">
                                            <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                 fill="none"
                                                 xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                      d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                                                      fill="#667085"/>
                                            </svg>

                                            <div style="font-size: 18px;">
                                                Other HCPs in account
                                            </div>
                                        </div>
                                    </div>
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Speciality</th>
                                                <th>Email</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% if other_hcps|length == 0 %}
                                                <tr>
                                                    <td colspan="3">
                                                        No data available
                                                    </td>
                                                </tr>
                                            {% endif %}
                                            {% for other_hcp in other_hcps %}
                                            <tr>
                                                <td>{{ other_hcp.name }}</td>
                                                <td class="color-secondary">
                                                    {{ other_hcp.specialty }}
                                                </td>
                                                <td class="color-secondary">
                                                    {{ other_hcp.email }}
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>

                                <div class="card no-split">
                                    <div class="card__table-header-wrapper">
                                        <div class="card__table-header">
                                            <svg class="icon" width="20" height="20" viewBox="0 0 20 20"
                                                 fill="none"
                                                 xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" clip-rule="evenodd"
                                                      d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                                                      fill="#667085"/>
                                            </svg>
                                            <div style="font-size: 18px;">
                                                Previous Account Visits
                                            </div>
                                        </div>
                                    </div>
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>Employee</th>
                                                <th>HCP</th>
                                                <th>Date</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% if interactions.previous_visits|length == 0 %}
                                                <tr>
                                                    <td colspan="3">
                                                        No data available
                                                    </td>
                                                </tr>
                                            {% endif %}
                                            {% for visit in interactions.previous_visits %}
                                            <tr>
                                                <td>{{ visit.employee_name }}</td>
                                                <td>{{ visit.hcp_name }}</td>
                                                <td class="color-secondary">{{ visit.date }}</td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div style="margin-top: 10px;"></div>
                        </main>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <td>
                        <div class="footer-space">&nbsp;</div>
                    </td>
                </tr>
            </tfoot>
        </table>
    </div>

    <footer style="padding: 20px; background: #DEFAF7; text-align:center;">
        <p style="margin: 0 0 5px;">
            Report generation supported by GenAI (generated on {{current_date}})
        </p>
        <small style="display: block; font-size: 12px; margin-top: 4px;">
            See Risks and Limitations <a style="text-decoration: underline" target="_blank" href="https://collaboration.merck.com/sites/lemon/SitePages/GPTeal-Risks-%26-Limitations.aspx"><strong>here</strong></a>
        </small>
        <small style="display: block; font-size: 12px; margin-top: 4px;">
            Submit your feedback and/or report any inaccuracies <a style="text-decoration: underline" target="_blank" href="https://forms.office.com/r/70hKAMf9ii"><strong>here</strong></a>
        </small>
        <small style="display: block; font-size: 12px; margin-top: 4px;">
            <strong>Powered by ai.MATE</strong>
        </small>
    </footer>
</div>
</body>
</html>
    """
)
