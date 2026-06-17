import createNextIntlPlugin from "next-intl/plugin";

// Point the plugin at our i18n request configuration.
const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {};

export default withNextIntl(nextConfig);
