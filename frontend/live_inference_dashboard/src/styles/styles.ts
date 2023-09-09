import { StyleDeclaration } from "aphrodite";

export const colors = {
  text_color: 'black',
  blue: "#000099",
  white: "#ffffff",
  light_grey: "#eff7f7",
  dark_grey: "#616161",
  dark_blue: "#252c39",
  light_blue: "#60CAD4",
  light_orange: "#FCAA8E",
};

export const sizes = {
  header: 60,
  simInfo: 37
};

interface StylesContainer {
  [index: string]: StyleDeclaration;
};

export const styles: StylesContainer = {
  card_style: {
    padding: 5,
    margin: 15,
    borderRadius: 3,
    height: '100%',
    backgroundColor: colors.white,
    borderColor: colors.white,
  },
  container_styles: {
  },
  header_styles: {
    marginLeft: 10,
    padding: 20,
    margin: 5,
    width: '100%',
    color: colors.text_color,
    fontSize: 25,
    float: 'left',
    clear: 'right',
    backgroundColor: colors.white,
    borderColor: colors.white,
    display: 'flex',
  },
  col_styles: {
    backgroundColor: '#5BC0F8',
    borderRadius: 10,
    margin: 5,
    padding: 10,
    float: "left",
  },
  row_styles: {
    borderRadius: 10,
    margin: 5,
    padding: 1,
    float: 'left',
    width: '100%',
    border: '1px solid #999999',
  },
  text_style: {
    paddingTop: 5,
    paddingRight: 0,
    paddingBottom: 0,
    paddingLeft: 0,
    margin: 5,
    fontSize: 20,
    color: '#8f979a'
  },
  button_styles: {
    backgroundColor: '#0081C9',
    borderRadius: 3,
    padding: 10,
    margin: 5,
    borderColor: 'transparent',
    width: '7em',
    fontWeight: 600
  }
}

export const modified_styles = {
  unpinned_button_styles: {
    ...styles.button_styles,
    backgroundColor: '#6a777d',
    borderColor: 'transparent',
  }
}
