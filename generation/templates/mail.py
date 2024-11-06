import jinja2

daily_email = jinja2.Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MSD</title>
</head>
<style>

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
        font-weight: 500;
        font-size: 14px;
        line-height: 1.4;
        color: #1A1C21;
    }

    body a {
        color: inherit;
        text-decoration: none;
    }

    .round-box {
        display: flex;
        align-items: center;
        padding: 10px 14px;
        border-radius: 8px;
        text-decoration: none;
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

    .round-box .icon {
        margin-right: 8px;
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
        display: block;
        width: 20px;
        height: 20px;
    }

    .card {
        border: 1px solid #E0E2E7;
        border-radius: 8px;
        box-shadow: 0 1.5px 2px 0 #1018281A;
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
        margin-right: 8px;
    }

    .badge {
        display: inline-flex;
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
        height: calc(110px);
    }

    .footer-space {
        height: calc(79px + 20px);
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
            <div style="float: right; text-align: right; width: 134px;">
                <svg style="display: block; width: 134px; height: 50px;" width="134" height="50" viewBox="0 0 134 50"
                     fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.5168 12.5C12.5168 9.18479 13.8356 6.00537 16.1829 3.66117C18.5303 1.31696 21.714 0 25.0337 0C28.3533 0 31.537 1.31696 33.8844 3.66117C36.2318 6.00537 37.5505 9.18479 37.5505 12.5H12.5168ZM12.5168 37.5C12.5168 34.1848 13.8356 31.0054 16.1829 28.6612C18.5303 26.317 21.714 25 25.0337 25C21.714 25 18.5303 23.683 16.1829 21.3388C13.8356 18.9946 12.5168 15.8152 12.5168 12.5C9.19716 12.5 6.01346 13.817 3.6661 16.1612C1.31873 18.5054 0 21.6848 0 25C0 28.3152 1.31873 31.4946 3.6661 33.8388C6.01346 36.183 9.19716 37.5 12.5168 37.5ZM12.5168 37.5C12.5168 40.8152 13.8356 43.9946 16.1829 46.3388C18.5303 48.683 21.714 50 25.0337 50C28.3533 50 31.537 48.683 33.8844 46.3388C36.2318 43.9946 37.5505 40.8152 37.5505 37.5H12.5168ZM25.0337 25C28.3533 25 31.537 26.317 33.8844 28.6612C36.2318 31.0054 37.5505 34.1848 37.5505 37.5C39.1942 37.5 40.8219 37.1767 42.3405 36.5485C43.8591 35.9203 45.2389 34.9996 46.4012 33.8388C47.5635 32.6781 48.4855 31.3001 49.1145 29.7835C49.7436 28.267 50.0673 26.6415 50.0673 25C50.0673 23.3585 49.7436 21.733 49.1145 20.2165C48.4855 18.6999 47.5635 17.3219 46.4012 16.1612C45.2389 15.0004 43.8591 14.0797 42.3405 13.4515C40.8219 12.8233 39.1942 12.5 37.5505 12.5C37.5505 15.8152 36.2318 18.9946 33.8844 21.3388C31.537 23.683 28.3533 25 25.0337 25Z"
                          fill="#009484"/>
                    <path d="M81.6181 12.5H89.3727V37.497H83.6241V20.6853L76.2719 37.497L68.5324 20.6641V37.497H63.1711V12.5H70.8349L76.3627 25.4381L81.6181 12.5ZM109.829 19.8846C109.829 14.9444 106.025 12.0861 101.481 12.0861C96.9366 12.0861 92.0624 14.7208 92.0624 19.8393C92.0624 24.2779 96.9548 26.5591 99.7474 27.2782C101.281 27.6831 105.151 28.1152 105.151 30.8769C105.151 33.5025 102.446 34.2186 100.422 34.2186C97.814 34.2186 96.2831 32.4057 96.507 29.635H91.3726C91.1941 35.8533 95.4268 38.1708 100.371 38.2856C106.086 38.4155 110.449 35.9772 110.449 30.481C110.449 24.9849 105.499 24.0845 101.629 22.8306C100.147 22.332 97.3632 21.8999 97.3632 19.3377C97.3632 17.2015 99.2088 16.1802 101.097 16.1802C103.517 16.1802 104.785 17.3888 104.966 19.8725H109.829M120.645 12.4607H112.667V37.4335H120.642C127.271 37.4335 134 33.6083 134 24.9698C134 16.3313 127.271 12.4728 120.642 12.4728L120.645 12.4607ZM120.285 32.8892H118.076V17.0625H120.285C126.363 17.0625 128.557 21.0207 128.557 24.9819C128.557 28.9431 126.36 32.9013 120.282 32.9013L120.285 32.8892Z"
                          fill="#243444"/>
                </svg>
            </div>
        </header>
        <table>
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
                        <h1>Your HCP Visit Insights</h1>

                        <h3>Hello {{ employee.name }}</h3>

                        <p style="margin: 0 0 30px; max-width: 100%;">
                            We've put together some helpful reports for your upcoming visits, you will find them
                            attached to this email.
                        </p>


                        <div style="margin-top: 30px;"></div>

                        <div style="display: flex; gap: 24px;">
                            <div
                                    style="flex: 0 0 auto; width: 100%; display: flex; flex-direction: column; gap: 24px;"
                            >
                                <div class="card no-split">
                                    <div style="padding: 18px 20px;">
                                        <div
                                                style="display: flex; align-items: center; justify-content: space-between;"
                                        >
                                            <div style="display: flex; align-items: center; gap: 12px;">
                                                <svg class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none"
                                                     xmlns="http://www.w3.org/2000/svg">
                                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                                          d="M2.5 5C2.5 3.61929 3.61929 2.5 5 2.5H15C16.3807 2.5 17.5 3.61929 17.5 5V15C17.5 16.3807 16.3807 17.5 15 17.5H5C3.61929 17.5 2.5 16.3807 2.5 15V5ZM15 4.16667H13.125V6.875H15.8333V5C15.8333 4.53976 15.4602 4.16667 15 4.16667ZM11.4583 4.16667V6.875H8.54167V4.16667H11.4583ZM11.4583 8.54167H8.54167V11.4583H11.4583V8.54167ZM11.4583 13.125H8.54167V15.8333H11.4583V13.125ZM6.875 11.4583V8.54167H4.16667V11.4583H6.875ZM4.16667 13.125H6.875V15.8333H5C4.53976 15.8333 4.16667 15.4602 4.16667 15V13.125ZM15.8333 13.125V15C15.8333 15.4602 15.4602 15.8333 15 15.8333H13.125V13.125H15.8333ZM15.8333 11.4583H13.125V8.54167H15.8333V11.4583ZM6.875 4.16667V6.875H4.16667V5C4.16667 4.53976 4.53976 4.16667 5 4.16667H6.875Z"
                                                          fill="#667085"/>
                                                </svg>
                                                <div style="font-size: 18px;">
                                                    Your agenda
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <table class="table">
                                        <thead>
                                        <tr>
                                            <th>Date and time</th>
                                            <th>Name</th>
                                            <th>Location</th>
                                            <th>Number of key points</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {% for visit in visits %}
                                        <tr>
                                            <td class="color-secondary">
                                                <span>{{visit.date}}</span>
                                            </td>
                                            <td class="color-secondary">
                                                <span>{{visit.hcp.name}}</span>
                                            </td>
                                            <td class="color-secondary">
                                                <span>{{visit.account.formatted_address}}</span>
                                            </td>
                                            <td>
                                                <span>{{visit.key_points}}</span>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                        </tbody>
                                    </table>
                                </div>

                                <div style="display: flex; gap: 16px;">
                                    <div>
                                        <div>
                                            <p>
                                                That wraps things up for now. Have a fantastic day and all the best with
                                                your visits!
                                            </p>
                                        </div>
                                    </div>
                                </div>

                            </div>
                            <div style="margin-top: 10px;"></div>
                        </div>
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
        <small style="display: block; font-size: 12px;">
            This is an automated message. Please do not reply.
        </small>
        <small style="display: block; font-size: 12px;">
            Submit your feedback and/or report any inaccuracies <a style="text-decoration: underline"
                                                                   href="https://forms.office.com/r/70hKAMf9ii"><strong>here</strong></a>
        </small>
        <small style="display: block; font-size: 12px;">
            <strong>Powered by ai.MATE</strong>
        </small>
    </footer>
</div>
</body>
</html>

""")
